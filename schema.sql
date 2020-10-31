DROP TABLE IF EXISTS student_info;
DROP TABLE IF EXISTS manager_info;
DROP TABLE IF EXISTS seat_info;
DROP TABLE IF EXISTS seat_leave_briefly;

-- table of student info
CREATE TABLE student_info(
	student_id INT PRIMARY KEY	NOT NULL,
	student_name TEXT NOT NULL
);

-- manager info
CREATE TABLE manager_info(
	manager_id INT PRIMARY KEY	NOT NULL,
	manager_name TEXT NOT NULL
);

-- table of seat info
CREATE TABLE seat_info(
    seat_id	INT PRIMARY KEY	NOT NULL,
    FOREIGN KEY (user_id) REFERENCES student_info (student_id)
    seat_status INT NOT NULL,
    seat_TYPE INT NOT NULL,
    seat_row INT NOT NULL,
    seat_col INT NOT NULL
);

-- table of breifly leaved seat
CREATE TABLE seat_leave_briefly(
    id INT PRIMARY NOT NULL,
    -- seat_id INT PRIMARY KEY NOT NULL,
    FOREIGN KEY (seat_id) REFERENCES seat_info (seat_id)
    -- user_id INT PRIMARY KEY NOT NULL,
    FOREIGN KEY (user_id) REFERENCES student_info (student_id)
    leave_time TEXT
)