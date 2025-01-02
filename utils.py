import pandas as pd


def tweak_attend(df):
    return (
        df.assign(
            Teacher=lambda df_: df_.CU.astype("str") + " - " + df_.TE,
            StudentName=lambda df_: (
                df_.LN + ", " + df_.FN + " " + df_.MN.str[0].fillna("")
            ).str.strip(),
            TDY=lambda df_: df_.COUNTX.where(df_.AL == "T", None),
            UNX=lambda df_: df_.COUNTX.where(df_.AL == "U", None),
            EXC=lambda df_: df_.COUNTX.where(df_.AL == "X", None),
            Phone=lambda df_: df_.TL.str.replace(
                r"(\d{3})(\d{3})(\d{4})", r"(\1) \2-\3", regex=True
            ),
            Grade=lambda df_: df_.GR.astype("str")
            .str.replace("0", "K")
            .replace("-1", "TK")
            .replace("17", "PS"),
        )
        .groupby("StudentName")
        .first()
        .reset_index()
        .sort_values(["TE", "LN"])
        .reset_index()
        .loc[
            :,
            [
                "Teacher",
                "ID",
                "StudentName",
                "Grade",
                "PG",
                "Phone",
                "TDY",
                "UNX",
                "EXC",
                "COUNTABSENCE",
            ],
        ]
        .rename(
            columns={
                "ID": "Student ID",
                "StudentName": "Student Name",
                "PG": "Parent/Guardian",
                "COUNTABSENCE": "TOTAL",
            }
        )
    )


def tweak_attend_flex(df):
    if df.empty:
        return pd.DataFrame(
            columns=[
                "Stu ID",
                "Student Name",
                "Grd",
                "Parent/Guardian",
                "Primary Phone",
                "Total",
                "Period",
                "Course",
                "Title",
                "Abs",
            ],
        )

    def group_func(grp):
        period_absences = grp.groupby(["STI", "CO"]).agg(Abs=("DT", "count"))
        if period_absences.max().Abs < 2:
            return None
        return period_absences

    return (
        df.assign(
            StudentName=lambda df_: (
                df_.LN + ", " + df_.FN + " " + df_.MN.str[0].fillna("")
            ).str.strip(),
        )
        .groupby(["ID", "StudentName", "GR", "PG", "TL"])
        .apply(group_func)
        .dropna()
        .assign(
            Total=lambda df_: df_.groupby(["ID", "StudentName", "GR", "PG", "TL"]).agg(
                Total=("Abs", "sum")
            )
        )
        .reset_index()
        .assign(
            TL=lambda df_: df_.TL.str.replace(
                r"(\d{3})(\d{3})(\d{4})", r"(\1) \2-\3", regex=True
            ),
        )
        .rename(
            columns={
                "GR": "Grd",
                "PG": "Parent/Guardian",
                "TL": "Primary Phone",
                "STI": "Period",
                "CO": "Course Title",
                "ID": "Stu ID",
                "StudentName": "Student Name",
            }
        )
        .set_index(
            [
                "Stu ID",
                "Student Name",
                "Grd",
                "Parent/Guardian",
                "Primary Phone",
                "Total",
                "Period",
            ]
        )
    )


def tweak_attend_middle(df):
    return (
        df.sort_values("StudentName")
        .assign(
            TL=lambda df_: df_.Telephone.str.replace(
                r"(\d{3})(\d{3})(\d{4})", r"(\1) \2-\3", regex=True
            ),
        )
        .loc[
            :,
            [
                "ID",
                "StudentName",
                "Grade",
                "Parent",
                "TL",
                "P1 Absences",
                "P2 Absences",
                "P3 Absences",
                "P4 Absences",
                "P5 Absences",
                "P6 Absences",
                "TotalAbsences",
            ],
        ]
        .rename(
            columns={
                "StudentName": "Student Name",
                "Grade": "Grd",
                "Paret": "Parent/Guardian",
                "TL": "Primary Phone",
                "TotalAbsences": "Total",
            }
        )
    )
