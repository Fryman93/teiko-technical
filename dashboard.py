import pandas as pd
import streamlit as st

st.set_page_config(page_title="Miraclib Response Analysis", layout="wide")

OUTPUTS = "outputs"

# ---------------------------------------------------------------------------
# Small helper so a missing file gives a friendly message instead of a crash
# (useful if make pipeline hasn't been run yet, or a filename changes later)
# ---------------------------------------------------------------------------
def load_csv(name):
    path = f"{OUTPUTS}/{name}"
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        st.warning(f"Missing `{path}` -- run `make pipeline` first.")
        return None


st.title("Loblaw Bio -- Miraclib Immune Cell Analysis")

tab2, tab3, tab4 = st.tabs(["Part 2 -- Cell Frequencies",
                            "Part 3 -- Statistical Analysis",
                            "Part 4 -- Subset Breakdown"])

# ---------------------------------------------------------------------------
# Part 2 -- relative frequency summary table
# ---------------------------------------------------------------------------
with tab2:
    st.header("Relative Frequency of Each Cell Population per Sample")
    df_summary = load_csv("pt2_initial_analysis.csv")
    if df_summary is not None:
        st.dataframe(df_summary, use_container_width=True)
        st.caption(f"{df_summary['sample'].nunique()} samples x "
                   f"{df_summary['population'].nunique()} populations")

# ---------------------------------------------------------------------------
# Part 3 -- boxplot, distribution plot, normality, and significance results
# ---------------------------------------------------------------------------
with tab3:
    st.header("Responders vs. Non-Responders")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Boxplot by Population")
        try:
            st.image(f"{OUTPUTS}/pt3_cell_box_plots.png", use_container_width=True)
        except FileNotFoundError:
            st.warning("Missing pt3_cell_box_plots.png -- run `make pipeline` first.")
    with col2:
        st.subheader("Distribution (KDE) by Population")
        try:
            st.image(f"{OUTPUTS}/pt3_cell_dist_plots.png", use_container_width=True)
        except FileNotFoundError:
            st.warning("Missing pt3_cell_dist_plots.png -- run `make pipeline` first.")

    st.subheader("Normality Check (Shapiro-Wilk)")
    df_shapiro = load_csv("pt3_shapiro_results.csv")
    if df_shapiro is not None:
        st.dataframe(
            df_shapiro.style.format({"W": "{:.3f}", "p_value": "{:.3g}"}),
            use_container_width=True,
        )

    st.subheader("Significance Testing (Mann-Whitney U + Welch's t-test)")
    df_mwu = load_csv("pt3_sig_results.csv")
    if df_mwu is not None:
        display = df_mwu.copy()
        display["U_p_value"] = display["U_p_value"].apply(lambda x: f"{x:.3g}")
        display["t_p_value"] = display["t_p_value"].apply(lambda x: f"{x:.3g}")
        st.dataframe(display, use_container_width=True)

        n_sig = (df_mwu["U_p_value"] < 0.05).sum()
        if n_sig == 0:
            st.info("No cell population shows a statistically significant "
                    "difference in relative frequency between responders and "
                    "non-responders at baseline using PBMC samples (all p >= 0.05 for both tests).")
        else:
            sig_pops = df_mwu.loc[df_mwu["U_p_value"] < 0.05, "population"].tolist()
            st.success(f"Significant difference found in: {', '.join(sig_pops)}")

# ---------------------------------------------------------------------------
# Part 4 -- subset breakdown (melanoma, PBMC, baseline, miraclib)
# ---------------------------------------------------------------------------
with tab4:
    st.header("Melanoma + PBMC + Baseline + Miraclib Subset")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Samples per Project")
        df_prj = load_csv("pt4_num_samples_per_prj.csv")
        if df_prj is not None:
            st.dataframe(df_prj, use_container_width=True)
            #st.bar_chart(df_prj.set_index("project"))

    with col2:
        st.subheader("Responders vs. Non-Responders")
        df_response = load_csv("pt4_num_responders.csv")
        if df_response is not None:
            st.dataframe(df_response, use_container_width=True)
            #st.bar_chart(df_response.set_index("response"))

    with col3:
        st.subheader("Sex Breakdown")
        df_gender = load_csv("pt4_num_gender.csv")
        if df_gender is not None:
            st.dataframe(df_gender, use_container_width=True)
            #st.bar_chart(df_gender.set_index("sex"))