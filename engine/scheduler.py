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
        
        # ---------------------------------------------------------
        # 1. PRE-CHECK: Ensure data is mathematically solvable
        # ---------------------------------------------------------
        for batch in self.batches:
            valid_rooms = [r for r in self.rooms if r.capacity >= batch.student_strength]
            if not valid_rooms:
                return False, f"Error: Batch {batch.semester_level}-{batch.section_name} has {batch.student_strength} students, but no room is large enough."
                
        # ---------------------------------------------------------
        # 2. CREATE VARIABLES (The Grid)
        # ---------------------------------------------------------
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

        for lesson in lessons:
            capable_teachers = [t for t in self.teachers if any(s.id == lesson["subject_id"] for s in t.subjects_can_teach)]
            if not capable_teachers:
                return False, f"Error: No teacher assigned for subject ID {lesson['subject_id']}"

            valid_rooms = [r for r in self.rooms if r.capacity >= lesson["strength"] and r.is_lab == lesson["requires_lab"]]
            
            for teacher in capable_teachers:
                for room in valid_rooms:
                    for d_idx, day in enumerate(self.days):
                        for slot in self.slots:
                            
                            # Calculate the actual 24h format time for this slot
                            actual_hour = self.open_hour + slot
                            
                            # --- IUB SPECIFIC CONSTRAINT: ROOM AVAILABILITY ---
                            # Only create a variable if the specific room is open during this hour
                            if actual_hour < room.available_from.hour or actual_hour >= room.available_to.hour:
                                continue

                            # --- IUB SPECIFIC CONSTRAINT: JUMMA BREAK ---
                            # Block both 13:00 (1 PM) and 14:00 (2 PM) on Fridays
                            if day == "Friday" and actual_hour in [13, 14]:
                                continue

                            var_name = f"{lesson['id']}_T{teacher.id}_R{room.id}_D{d_idx}_S{slot}"
                            self.schedule_vars[(lesson["id"], teacher.id, room.id, d_idx, slot)] = self.model.NewBoolVar(var_name)

        # ---------------------------------------------------------
        # 3. ADD HARD CONSTRAINTS
        # ---------------------------------------------------------
        
        # Constraint A: Every lesson scheduled exactly ONCE
        for lesson in lessons:
            lesson_vars = [var for key, var in self.schedule_vars.items() if key[0] == lesson["id"]]
            if not lesson_vars:
                return False, f"Conflict: {lesson['id']} cannot be scheduled due to room/time restrictions."
            self.model.AddExactlyOne(lesson_vars)

        # Constraint B: One teacher per slot
        for teacher in self.teachers:
            for d_idx in range(len(self.days)):
                for slot in self.slots:
                    teacher_slot_vars = [var for key, var in self.schedule_vars.items() if key[1] == teacher.id and key[3] == d_idx and key[4] == slot]
                    self.model.AddAtMostOne(teacher_slot_vars)

        # Constraint C: One room per slot
        for room in self.rooms:
            for d_idx in range(len(self.days)):
                for slot in self.slots:
                    room_slot_vars = [var for key, var in self.schedule_vars.items() if key[2] == room.id and key[3] == d_idx and key[4] == slot]
                    self.model.AddAtMostOne(room_slot_vars)

        # Constraint D: One batch per slot
        for batch in self.batches:
            for d_idx in range(len(self.days)):
                for slot in self.slots:
                    batch_slot_vars = [var for key, var in self.schedule_vars.items() if key[0].startswith(f"B{batch.id}_") and key[3] == d_idx and key[4] == slot]
                    self.model.AddAtMostOne(batch_slot_vars)

        # ---------------------------------------------------------
        # 4. SOLVE THE MODEL
        # ---------------------------------------------------------
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0 
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            final_schedule = []
            for key, var in self.schedule_vars.items():
                if solver.Value(var) == 1:
                    lesson_id, t_id, r_id, d_idx, slot = key
                    actual_hour = self.open_hour + slot
                    
                    batch_id = int(lesson_id.split('_')[0][1:])
                    subject_id = int(lesson_id.split('_')[1][1:])
                    
                    final_schedule.append({
                        "batch_id": batch_id,
                        "subject_id": subject_id,
                        "teacher_id": t_id,
                        "room_id": r_id,
                        "day": self.days[d_idx],
                        "start_time": f"{actual_hour:02d}:00",
                        "end_time": f"{(actual_hour + 1):02d}:00"
                    })
            return True, final_schedule
        else:
            return False, "Could not find a clash-free combination. Check if Room availability windows are too small."
