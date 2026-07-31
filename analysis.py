# %%
import pandas as pd
import sqlite3
import seaborn as sns
import scipy.stats as stats
import matplotlib.pyplot as plt

# %%
# Part 2 - Initial Analysis
conn = sqlite3.connect('loblaw.db')
df_summary = pd.read_sql("""
    SELECT
        sample,
        SUM(count) OVER (PARTITION BY sample) AS total_count,
        population,
        count,
        ROUND(100.0 * count / SUM(count) OVER (PARTITION BY sample), 2) AS percentage
    FROM cell_counts
    ORDER BY sample, population;
""", conn)
df_summary.to_csv("outputs/pt2_initial_analysis.csv", index=False)

# %%
# Part 3 - Statistical Analysis
compare_cell_pop = pd.read_sql("""
    SELECT
        cc.sample,
        SUM(cc.count) OVER (PARTITION BY cc.sample) AS total_count,
        cc.population,
        cc.count,
        ROUND(100.0 * cc.count / SUM(cc.count) OVER (PARTITION BY cc.sample), 2) AS percentage,
        s.sample_type,
        sub.condition,
        sub.treatment,
        sub.response
    FROM cell_counts cc
    LEFT JOIN samples s ON cc.sample = s.sample
    LEFT JOIN subjects sub ON s.subject = sub.subject
    WHERE
        sub.condition = 'melanoma'
        AND s.sample_type = 'PBMC'
        AND s.time_from_treatment_start = 0
        AND sub.treatment = 'miraclib'
    ORDER BY cc.sample, cc.population;
""", conn)
compare_cell_pop.to_csv('outputs/pt3_compare_cell_pop.csv', index=False)

# %%
plt.rcParams["font.weight"] = "normal"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.titleweight"] = "bold"


def make_cell_dist_plots(table):
    g = sns.FacetGrid(table, col='population', hue='response')
    g.map_dataframe(sns.kdeplot, x='percentage')
    g.add_legend()
    g.figure.savefig("outputs/pt3_cell_dist_plots.png", dpi=150, bbox_inches="tight")
    plt.close(g.figure)


make_cell_dist_plots(compare_cell_pop)


# %%
def make_cell_box_plots(table):
    fig, axes = plt.subplots(figsize=(15, 8))
    sns.boxplot(data=table, x='population',
                y='percentage', hue='response', ax=axes)
    axes.set_title("Cell Population Relative Frequencies: Responders vs. Non-Responders",
                    fontsize=16, fontweight="bold")
    fig.savefig("outputs/pt3_cell_box_plots.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


make_cell_box_plots(compare_cell_pop)


# %%
def check_dist(table):
    def check_dist_group(group):
        stat, p_value = stats.shapiro(group["percentage"])
        return pd.Series({"W": stat, "p_value": p_value, "is_normal": p_value >= 0.05})

    shapiro_results = table.groupby(["population", "response"]).apply(check_dist_group).reset_index()
    shapiro_results.to_csv("outputs/pt3_shapiro_results.csv", index=False)
    return shapiro_results


shapiro_results = check_dist(compare_cell_pop)


# %%
def check_sig(table):
    def check_sig_group(group):
        yes = group[group["response"] == 'yes']["percentage"]
        no = group[group["response"] == 'no']["percentage"]
        u_stat, u_p_value = stats.mannwhitneyu(yes, no)
        t_stat, t_p_value = stats.ttest_ind(yes, no, equal_var=False)
        return pd.Series({
            "U_stat": u_stat, "U_p_value": u_p_value,
            "t_stat": t_stat, "t_p_value": t_p_value
        })

    result = table.groupby("population").apply(check_sig_group).reset_index()
    result.to_csv("outputs/pt3_sig_results.csv", index=False)
    return result


mann_results = check_sig(compare_cell_pop)

# %%
# Part 4 - Data Subset Analysis:
melanoma_pmbc_baseline = pd.read_sql("""
    SELECT
        s.sample,
        s.sample_type,
        s.time_from_treatment_start,
        sub.subject,
        sub.project,
        sub.condition,
        sub.age,
        sub.sex,
        sub.treatment,
        sub.response
    FROM samples s
    LEFT JOIN subjects sub ON s.subject = sub.subject
    WHERE
        sub.condition = 'melanoma'
        AND s.sample_type = 'PBMC'
        AND s.time_from_treatment_start = 0
        AND sub.treatment = 'miraclib';
""", conn)

# %%
num_samples_per_prj = pd.read_sql("""
    SELECT project, COUNT(*) AS num_samples
    FROM samples s
    LEFT JOIN subjects sub ON s.subject = sub.subject
    WHERE
        sub.condition = 'melanoma'
        AND s.sample_type = 'PBMC'
        AND s.time_from_treatment_start = 0
        AND sub.treatment = 'miraclib'
    GROUP BY project;
""", conn)
num_samples_per_prj.to_csv("outputs/pt4_num_samples_per_prj.csv", index=False)

# %%
num_responders = pd.read_sql("""
    SELECT response, COUNT(*) AS num_responses
    FROM samples s
    LEFT JOIN subjects sub ON s.subject = sub.subject
    WHERE
        sub.condition = 'melanoma'
        AND s.sample_type = 'PBMC'
        AND s.time_from_treatment_start = 0
        AND sub.treatment = 'miraclib'
    GROUP BY response;
""", conn)
num_responders.to_csv("outputs/pt4_num_responders.csv", index=False)

# %%
num_gender = pd.read_sql("""
    SELECT sex, COUNT(*) AS num_subjects
    FROM samples s
    LEFT JOIN subjects sub ON s.subject = sub.subject
    WHERE
        sub.condition = 'melanoma'
        AND s.sample_type = 'PBMC'
        AND s.time_from_treatment_start = 0
        AND sub.treatment = 'miraclib'
    GROUP BY sex;
""", conn)
num_gender.to_csv("outputs/pt4_num_gender.csv", index=False)

# %%
avg_melanoma_male_time0_bcells = pd.read_sql("""
    SELECT ROUND(AVG(cc.count), 2) AS avg_b_cell_count
    FROM cell_counts cc
    LEFT JOIN samples s ON cc.sample = s.sample
    LEFT JOIN subjects sub ON s.subject = sub.subject
    WHERE
        sub.condition = 'melanoma'
        AND s.time_from_treatment_start = 0
        AND sub.sex = 'M'
        AND sub.response = 'yes'
        AND cc.population = 'b_cell';
""", conn)

conn.close()