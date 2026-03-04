from ortools.sat.python import cp_model
from database.crud import get_all_teachers, get_all_rooms, get_all_subjects, get_all_batches, get_global_settings
from datetime import datetime, time

class TimetableEngine:
    def __init__(self, db_session):
        self.session = db_session
        self.model = cp_model.CpModel()
        self.settings = get_global_settings(db_session)
        
        # Load all data
        self.teachers = get_all_teachers(db_session)
        self.rooms = get_all_rooms(db_session)
        self.batches = get_all_batches(db_session)
        self.subjects = get_all_subjects(db_session)
        
        # Scheduling configuration
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        if not self.settings.sunday_off:
            self.days.append("Sunday")
            
        # Calculate timeslots based on university hours
        self.open_hour = self.settings.uni_open_time.hour
        self.close_hour = self.settings.uni_close_time.hour
        self.num_slots_per_day = self.close_hour - self.open_hour
        
        self.slots = list(range(self.num_slots_per_day))
        
        # Dictionary to store all our generated boolean variables
        self.schedule_vars = {}
        
    def generate(self):
        """Builds the constraints and solves the timetable."""
        
        # 1. PRE-CHECK: Batch room capacity check
        for batch in self.batches:
            valid_rooms = [r for r in self.rooms if r.capacity >= batch.student_strength]
            if not valid_rooms:
                return False, f"Error: Batch {batch.semester_level}-{batch.section_name} (Strength: {batch.student_strength}) has no room large enough."

        # 2. CREATE LESSON LIST
        lessons = []
        for batch in self.batches:
            for subject in batch.curriculum_subjects:
                for part in range(subject.total_credit_hours):
                    lesson_id = f"B{batch.id}_S{subject.id}_P{part}"
                    lessons.append({
                        "id": lesson_id,
                        "batch_id": batch.id,
                        "subject_id": subject.id,
                        "requires_lab": subject.requires_lab,
                        "strength": batch.student_strength
                    })

        # 3. VARIABLE GENERATION WITH PLACEHOLDERS
        for lesson in lessons:
            # Check for capable teachers
            capable_teachers = [t for t in self.teachers if any(s.id == lesson["subject_id"] for s in t.subjects_can_teach)]
            
            # If no teacher assigned, use Dummy ID -1
            teacher_ids = [t.id for t in capable_teachers] if capable_teachers else [-1]

            # Check for valid rooms
            valid_rooms = [r for r in self.rooms if r.capacity >= lesson["strength"] and r.is_lab == lesson["requires_lab"]]
            
            # If no room assigned, use Dummy Room ID -1
            if not valid_rooms:
                room_pool = [(-1, time(0,0), time(23,59))] # Dummy Room data
            else:
                room_pool = [(r.id, r.available_from, r.available_to) for r in valid_rooms]

            for t_id in teacher_ids:
                for r_id, r_from, r_to in room_pool:
                    for d_idx, day in enumerate(self.days):
                        for slot in self.slots:
                            actual_hour = self.open_hour + slot
                            
                            # Specific Room Availability (Skip only if not dummy)
                            if r_id != -1:
                                if actual_hour < r_from.hour or actual_hour >= r_to.hour:
                                    continue

                            # IUB Jumma Break
                            if day == "Friday" and actual_hour in [13, 14]:
                                continue

                            var_key = (lesson["id"], t_id, r_id, d_idx, slot)
                            var_name = f"{lesson['id']}_T{t_id}_R{r_id}_D{d_idx}_S{slot}"
                            self.schedule_vars[var_key] = self.model.NewBoolVar(var_name)

        # 4. HARD CONSTRAINTS
        # Constraint A: Every lesson must happen once
        for lesson in lessons:
            lesson_vars = [var for key, var in self.schedule_vars.items() if key[0] == lesson["id"]]
            if not lesson_vars:
                return False, f"Impossible: {lesson['id']} cannot be scheduled. Ensure teachers/rooms exist for this subject."
            self.model.AddExactlyOne(lesson_vars)

        # Constraint B: Teachers can't overlap (Except Dummy -1)
        for teacher in self.teachers:
            for d_idx in range(len(self.days)):
                for slot in self.slots:
                    t_vars = [var for key, var in self.schedule_vars.items() if key[1] == teacher.id and key[3] == d_idx and key[4] == slot]
                    self.model.AddAtMostOne(t_vars)

        # Constraint C: Rooms can't overlap (Except Dummy -1)
        for room in self.rooms:
            for d_idx in range(len(self.days)):
                for slot in self.slots:
                    r_vars = [var for key, var in self.schedule_vars.items() if key[2] == room.id and key[3] == d_idx and key[4] == slot]
                    self.model.AddAtMostOne(r_vars)

        # Constraint D: Batches can't overlap
        for batch in self.batches:
            for d_idx in range(len(self.days)):
                for slot in self.slots:
                    b_vars = [var for key, var in self.schedule_vars.items() if key[0].startswith(f"B{batch.id}_") and key[3] == d_idx and key[4] == slot]
                    self.model.AddAtMostOne(b_vars)

        # 5. SOLVE
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            final_schedule = []
            for key, var in self.schedule_vars.items():
                if solver.Value(var) == 1:
                    l_id, t_id, r_id, d_idx, slot = key
                    actual_hour = self.open_hour + slot
                    
                    final_schedule.append({
                        "batch_id": int(l_id.split('_')[0][1:]),
                        "subject_id": int(l_id.split('_')[1][1:]),
                        "teacher_id": t_id,
                        "room_id": r_id,
                        "day": self.days[d_idx],
                        "start_time": f"{actual_hour:02d}:00",
                        "end_time": f"{(actual_hour + 1):02d}:00"
                    })
            return True, final_schedule
        return False, "Could not find a valid combination. Check data constraints."
