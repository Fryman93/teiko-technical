import pandas as pd
import sqlite3

# Part 1 - Data Management
df = pd.read_csv("cell-count.csv")

conn = sqlite3.connect('loblaw.db')
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")
cur.executescript("""
CREATE TABLE IF NOT EXISTS subjects (
    subject TEXT PRIMARY KEY,
    project TEXT,
    condition TEXT,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    response TEXT
);

CREATE TABLE IF NOT EXISTS samples (
    sample TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    sample_type TEXT,
    time_from_treatment_start INTEGER,
    FOREIGN KEY (subject) REFERENCES subjects(subject)
);

CREATE TABLE IF NOT EXISTS cell_counts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample TEXT NOT NULL,
    population TEXT NOT NULL,
    count INTEGER NOT NULL,
    FOREIGN KEY (sample) REFERENCES samples(sample),
    UNIQUE (sample, population)
);
""")

df_subjects = df[['project', 'subject', 'condition', 'age',
                   'sex', 'treatment', 'response']].drop_duplicates()

df_samples = df[['sample', 'subject', 'sample_type', 'time_from_treatment_start']]

populations = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
df_cell_counts = df.melt(
    id_vars=['sample'],
    value_vars=populations,
    var_name='population',
    value_name='count'
)
# %%
df_subjects.to_sql("subjects", conn, if_exists="append", index=False)
df_samples.to_sql("samples", conn, if_exists="append", index=False)
df_cell_counts.to_sql("cell_counts", conn, if_exists="append", index=False)
conn.commit()
conn.close()