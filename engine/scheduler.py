import time

from ortools.sat.python import cp_model

from database.crud import get_all_teachers, get_all_rooms, get_all_subjects, get_all_batches, get_global_settings

from datetime import datetime, time as dt_time



class TimetableEngine:

    def __init__(self, db_session, status_callback=None):

        self.session = db_session

        self.status_callback = status_callback

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

        

        self.schedule_vars = {}



    def log(self, message):

        """Helper to send updates to the UI Console."""

        if self.status_callback:

            self.status_callback(message)



    def generate(self):

        start_time = time.time()

        self.log("🔍 Analyzing department constraints and room capacities...")

        

        # 1. PRE-CHECK: Batch room capacity check

        for batch in self.batches:

            valid_rooms = [r for r in self.rooms if r.capacity >= batch.student_strength]

            if not valid_rooms:

                return False, f"Error: Batch {batch.semester_level}-{batch.section_name} has no room large enough for {batch.student_strength} students."



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



        self.log(f"🏗️ Generating possible slots for {len(lessons)} weekly lessons...")



        # 3. VARIABLE GENERATION WITH PLACEHOLDERS

        for lesson in lessons:

            capable_teachers = [t for t in self.teachers if any(s.id == lesson["subject_id"] for s in t.subjects_can_teach)]

            teacher_ids = [t.id for t in capable_teachers] if capable_teachers else [-1]



            valid_rooms = [r for r in self.rooms if r.capacity >= lesson["strength"] and r.is_lab == lesson["requires_lab"]]

            if not valid_rooms:

                room_pool = [(-1, dt_time(0,0), dt_time(23,59))] 

            else:

                room_pool = [(r.id, r.available_from, r.available_to) for r in valid_rooms]



            for t_id in teacher_ids:

                for r_id, r_from, r_to in room_pool:

                    for d_idx, day in enumerate(self.days):

                        for slot in self.slots:

                            actual_hour = self.open_hour + slot

                            

                            if r_id != -1:

                                if actual_hour < r_from.hour or actual_hour >= r_to.hour:

                                    continue



                            if day == "Friday" and actual_hour in [13, 14]:

                                continue



                            var_key = (lesson["id"], t_id, r_id, d_idx, slot)

                            self.schedule_vars[var_key] = self.model.NewBoolVar(f"Var_{len(self.schedule_vars)}")



        self.log("⚖️ Enforcing clash-free rules and daily limits...")



        # 4. HARD CONSTRAINTS

        # Every lesson must happen exactly once

        for lesson in lessons:

            lesson_vars = [var for key, var in self.schedule_vars.items() if key[0] == lesson["id"]]

            if not lesson_vars:

                return False, f"Impossible: No valid slots for {lesson['id']}."

            self.model.AddExactlyOne(lesson_vars)



        # NEW: Daily hour limit per subject (spreads out 3-credit courses)

        max_h = getattr(self.settings, 'max_hours_per_day', 2)

        for batch in self.batches:

            for subject in batch.curriculum_subjects:

                for d_idx in range(len(self.days)):

                    daily_subject_vars = [

                        var for key, var in self.schedule_vars.items() 

                        if key[0].startswith(f"B{batch.id}_S{subject.id}_") and key[3] == d_idx

                    ]

                    if daily_subject_vars:

                        self.model.Add(sum(daily_subject_vars) <= max_h)



        # Overlap Prevention

        for teacher in self.teachers:

            for d_idx in range(len(self.days)):

                for slot in self.slots:

                    t_vars = [var for key, var in self.schedule_vars.items() if key[1] == teacher.id and key[3] == d_idx and key[4] == slot]

                    self.model.AddAtMostOne(t_vars)



        for room in self.rooms:

            for d_idx in range(len(self.days)):

                for slot in self.slots:

                    r_vars = [var for key, var in self.schedule_vars.items() if key[2] == room.id and key[3] == d_idx and key[4] == slot]

                    self.model.AddAtMostOne(r_vars)



        for batch in self.batches:

            for d_idx in range(len(self.days)):

                for slot in self.slots:

                    b_vars = [var for key, var in self.schedule_vars.items() if key[0].startswith(f"B{batch.id}_") and key[3] == d_idx and key[4] == slot]

                    self.model.AddAtMostOne(b_vars)



        self.log("🤖 AI is rapidly solving using all available CPU threads...")



        # 5. SOLVE WITH SPEED OPTIMIZATIONS

        solver = cp_model.CpSolver()

        solver.parameters.max_time_in_seconds = 15.0 

        

        # Unlocks multi-core parallel processing

        solver.parameters.num_search_workers = 12 

        

        # Strategy: Find first feasible solution immediately

        solver.parameters.search_branching = cp_model.FIXED_SEARCH 

        

        status = solver.Solve(self.model)



        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:

            self.log(f"✨ Success in {time.time() - start_time:.2f}s!")

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

        

        return False, "Timed out. Data may be too complex or over-constrained."
