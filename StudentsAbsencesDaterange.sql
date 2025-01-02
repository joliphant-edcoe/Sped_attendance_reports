WITH rawdata AS 
	(SELECT 
		STU.SC,
		STU.SN,
		STU.LN,
		STU.FN,
		STU.MN,
		STU.ID,
		STU.SX,
		STU.GR,
		STU.PG,
		STU.TL,
		STU.CU,
		ATT.AL,
		--ATT.SN,
		ATT.DT,
		ATT.DY,
		--TCH.SC,
		TCH.TN,
		TCH.TE,
		TCH.TF,
		TCH.EM
		--ATT.*,
		--STU.*
	FROM 
		(SELECT STU.* FROM STU WHERE DEL = 0) STU
	LEFT JOIN 
		(SELECT ATT.* FROM ATT WHERE DEL = 0) ATT 
		ON STU.SN = ATT.SN
		AND STU.SC = ATT.SC
	LEFT JOIN 
		(SELECT TCH.* FROM TCH WHERE DEL = 0) TCH 
		ON TCH.SC = STU.SC 
		AND TCH.TN = STU.CU
	WHERE 
		ATT.DT BETWEEN DATEADD(DAY, -((DATEPART(WEEKDAY, GETDATE()) + 5) % 7 + 7), CAST(GETDATE() AS DATE)) 
				   AND DATEADD(DAY, -((DATEPART(WEEKDAY, GETDATE()) + 1) % 7), CAST(GETDATE() AS DATE)) 
		AND ATT.AL > ' '
		AND STU.SC = 68  --68,73
	--ORDER BY SN
),
grouped_data AS (
	SELECT 
		TE,
		ID,
		COUNT(*) AS COUNTABSENCE
	FROM
		rawdata
	GROUP BY TE, ID
	HAVING COUNT(*) > 1
),
X_count AS (
	SELECT 
		TE,
		ID,
		AL,
		COUNT(*) AS COUNTX
	FROM
		rawdata
	GROUP BY TE, ID, AL
),
deduplicated AS (
	SELECT 
		rd.TE, 
		rd.CU,
		rd.ID, 
		rd.AL, 
		rd.TL, 
		rd.LN, 
		rd.FN, 
		rd.MN,
		rd.PG,
		rd.GR,
		gd.COUNTABSENCE, 
		xc.COUNTX,
		ROW_NUMBER() OVER (PARTITION BY rd.ID, rd.AL ORDER BY rd.DT DESC) AS row_num
	FROM 
		rawdata rd
	JOIN grouped_data gd
		ON rd.TE = gd.TE
		AND rd.ID = gd.ID
	JOIN X_count xc
		ON rd.TE = xc.TE
		AND rd.ID = xc.ID
		AND rd.AL = xc.AL
)
SELECT 
	TE, CU,ID, AL, GR, TL, LN, FN, MN,PG, COUNTABSENCE, COUNTX
FROM deduplicated
WHERE row_num = 1
ORDER BY TE,LN;



/*
SELECT 
	DATEADD(DAY, -((DATEPART(WEEKDAY, GETDATE()) + 5) % 7 + 7), CAST(GETDATE() AS DATE)) AS MostRecentMonday,
	DATEADD(DAY, -((DATEPART(WEEKDAY, GETDATE()) + 1) % 7), CAST(GETDATE() AS DATE)) AS MostRecentFriday;
*/