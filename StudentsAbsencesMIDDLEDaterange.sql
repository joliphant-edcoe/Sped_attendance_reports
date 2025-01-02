-- Step 1: Define base data extraction with meaningful names
-- Extracts student data, attendance records, and teacher information.
-- Filters out deleted records (DEL = 0) and limits attendance to the current week (Monday to Friday).
WITH StudentData AS (
    SELECT 
        STU.ID,                -- Student ID
        ATT.A1, ATT.A2, ATT.A3, ATT.A4, ATT.A5, ATT.A6,  -- Attendance Columns
        ATT.DT                 -- Attendance Date
    FROM 
        (SELECT * FROM STU WHERE DEL = 0) AS STU -- Students table filtered to active records
    LEFT JOIN 
        (SELECT * FROM ATT WHERE DEL = 0) AS ATT -- Attendance table filtered to active records
        ON STU.SN = ATT.SN AND STU.SC = ATT.SC
    WHERE 
        ATT.DT BETWEEN 
            DATEADD(DAY, -((DATEPART(WEEKDAY, GETDATE()) + 5) % 7 + 7), CAST(GETDATE() AS DATE)) -- Most recent Monday
            AND DATEADD(DAY, -((DATEPART(WEEKDAY, GETDATE()) + 1) % 7), CAST(GETDATE() AS DATE)) -- Most recent Friday
        AND STU.SC = 69     -- Limit to a specific school code
),

-- Step 2: Aggregate attendance counts for each student
-- Counts the non-blank attendance entries for the previous week, grouped by student ID.
AttendanceSummary AS (
    SELECT 
        ID,                                        -- Student ID
        COUNT(CASE WHEN TRIM(A1) <> '' THEN 1 END) AS [P1 Absences], -- Count of non-blank entries for A1
        COUNT(CASE WHEN TRIM(A2) <> '' THEN 1 END) AS [P2 Absences],
        COUNT(CASE WHEN TRIM(A3) <> '' THEN 1 END) AS [P3 Absences],
        COUNT(CASE WHEN TRIM(A4) <> '' THEN 1 END) AS [P4 Absences],
        COUNT(CASE WHEN TRIM(A5) <> '' THEN 1 END) AS [P5 Absences],
        COUNT(CASE WHEN TRIM(A6) <> '' THEN 1 END) AS [P6 Absences],
        (COUNT(CASE WHEN TRIM(A1) <> '' THEN 1 END) + 
         COUNT(CASE WHEN TRIM(A2) <> '' THEN 1 END) + 
         COUNT(CASE WHEN TRIM(A3) <> '' THEN 1 END) + 
         COUNT(CASE WHEN TRIM(A4) <> '' THEN 1 END) + 
         COUNT(CASE WHEN TRIM(A5) <> '' THEN 1 END) + 
         COUNT(CASE WHEN TRIM(A6) <> '' THEN 1 END)) AS TotalAbsences -- Sum of all attendance counts
    FROM 
        StudentData
    GROUP BY 
        ID
    HAVING 
        COUNT(CASE WHEN TRIM(A1) <> '' THEN 1 END) > 1 OR
        COUNT(CASE WHEN TRIM(A2) <> '' THEN 1 END) > 1 OR
        COUNT(CASE WHEN TRIM(A3) <> '' THEN 1 END) > 1 OR
        COUNT(CASE WHEN TRIM(A4) <> '' THEN 1 END) > 1 OR
        COUNT(CASE WHEN TRIM(A5) <> '' THEN 1 END) > 1 OR
        COUNT(CASE WHEN TRIM(A6) <> '' THEN 1 END) > 1
)

-- Step 3: Join aggregated attendance counts with student details
-- Combines attendance data with detailed student information for final output.
SELECT 
    STU.LN + ', ' + STU.FN AS StudentName,  -- Concatenates last and first name
    STU.GR AS Grade,                       -- Student grade
    STU.PG AS Parent,                      -- Parent/Guardian
    STU.TL AS Telephone,                   -- Primary phone number
	AttendanceSummary.*
FROM 
    (SELECT * FROM STU WHERE DEL = 0 AND NOT TG > '') AS STU -- Filter active student records
RIGHT JOIN 
    AttendanceSummary 
    ON STU.ID = AttendanceSummary.ID; -- Match on student ID
