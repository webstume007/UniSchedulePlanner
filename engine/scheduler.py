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
            
        # Calculate timeslots based on university hours (assuming 1 slot = 1 hour for simplicity here)
        open_hour = self.settings.uni_open_time.hour
        close_hour = self.settings.uni_close_time.hour
        self.num_slots_per_day = close_hour - open_hour
        
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
        # We break down every subject into individual 1-hour "lessons"
        lessons = []
        for batch in self.batches:
            for subject in batch.curriculum_subjects:
                # If a subject is 3 credit hours, we create 3 independent lessons
                for part in range(subject.total_credit_hours):
                    lesson_id = f"B{batch.id}_S{subject.id}_P{part}"
                    lessons.append({
                        "id": lesson_id,
                        "batch_id": batch.id,
                        "subject_id": subject.id,
                        "requires_lab": subject.requires_lab,
                        "strength": batch.student_strength
                    })

        # Create a boolean variable for every possible valid combination
        for lesson in lessons:
            # Find capable teachers for this specific subject
            capable_teachers = [t for t in self.teachers if any(s.id == lesson["subject_id"] for s in t.subjects_can_teach)]
            if not capable_teachers:
                return False, f"Error: No teacher assigned for subject ID {lesson['subject_id']}"

            # Find valid rooms (Must fit students, and must match Lab requirement)
            valid_rooms = [r for r in self.rooms if r.capacity >= lesson["strength"] and r.is_lab == lesson["requires_lab"]]
            
            for teacher in capable_teachers:
                for room in valid_rooms:
                    for d_idx, day in enumerate(self.days):
                        for slot in self.slots:
                            
                            # JUMMA BREAK LOGIC: 
                            # If Day is Friday (index 4) and slot overlaps with 1:00 PM (hour 13)
                            # Let's say uni opens at 8 AM. Slot 0 = 8 AM. Slot 5 = 1 PM.
                            actual_hour = open_hour + slot
                            if day == "Friday" and actual_hour >= self.settings.jumma_break_start.hour and actual_hour < self.settings.jumma_break_end.hour:
                                continue # Skip creating a variable for the Jumma gap entirely

                            var_name = f"{lesson['id']}_T{teacher.id}_R{room.id}_D{d_idx}_S{slot}"
                            self.schedule_vars[(lesson["id"], teacher.id, room.id, d_idx, slot)] = self.model.NewBoolVar(var_name)

        # ---------------------------------------------------------
        # 3. ADD HARD CONSTRAINTS
        # ---------------------------------------------------------
        
        # Constraint A: Every single lesson must be scheduled exactly ONCE
        for lesson in lessons:
            lesson_vars = []
            for key, var in self.schedule_vars.items():
                if key[0] == lesson["id"]:
                    lesson_vars.append(var)
            self.model.AddExactlyOne(lesson_vars)

        # Constraint B: A Teacher can only teach ONE class at a time
        for teacher in self.teachers:
            for d_idx in range(len(self.days)):
                for slot in self.slots:
                    teacher_slot_vars = [var for key, var in self.schedule_vars.items() if key[1] == teacher.id and key[3] == d_idx and key[4] == slot]
                    self.model.AddAtMostOne(teacher_slot_vars)

        # Constraint C: A Room can only host ONE class at a time
        for room in self.rooms:
            for d_idx in range(len(self.days)):
                for slot in self.slots:
                    room_slot_vars = [var for key, var in self.schedule_vars.items() if key[2] == room.id and key[3] == d_idx and key[4] == slot]
                    self.model.AddAtMostOne(room_slot_vars)

        # Constraint D: A Batch (Section) can only attend ONE class at a time
        for batch in self.batches:
            for d_idx in range(len(self.days)):
                for slot in self.slots:
                    batch_slot_vars = [var for key, var in self.schedule_vars.items() if key[0].startswith(f"B{batch.id}_") and key[3] == d_idx and key[4] == slot]
                    self.model.AddAtMostOne(batch_slot_vars)

        # ---------------------------------------------------------
        # 4. SOLVE THE MODEL
        # ---------------------------------------------------------
        solver = cp_model.CpSolver()
        # Set a time limit so the server doesn't freeze on impossible inputs
        solver.parameters.max_time_in_seconds = 30.0 
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract the winning schedule
            final_schedule = []
            for key, var in self.schedule_vars.items():
                if solver.Value(var) == 1:
                    lesson_id, t_id, r_id, d_idx, slot = key
                    actual_hour = open_hour + slot
                    
                    # Parse the lesson string "B1_S2_P0" back into readable data
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
            return False, "Algorithm could not find a clash-free combination with the current constraints. Try adding more rooms or teachers."
