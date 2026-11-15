import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_generator import generate_infra_portfolio, optimize_3c_allocation

st.set_page_config(
    page_title="B2B Infra & AI DC Margin Optimizer",
    page_icon="⚡",
    layout="wide",
)

# Custom CSS untuk nuansa eksekutif korporat (#0F172A, #0284C7, #DC2626)
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(90deg, #0F172A 0%, #1E293B 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: #F8FAFC;
        margin-bottom: 1rem;
        border-left: 6px solid #0284C7;
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .main-header p {
        margin: 0.35rem 0 0 0;
        font-size: 0.95rem;
        color: #CBD5E1;
    }
    .notice-banner {
        background-color: #FEF2F2;
        border-left: 5px solid #DC2626;
        padding: 0.85rem 1.2rem;
        border-radius: 6px;
        color: #7F1D1D;
        font-size: 0.88rem;
        margin-bottom: 1.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Utama
st.markdown(
    """
    <div class="main-header">
        <h1>AI Data Center & Telco Infrastructure Margin Optimizer</h1>
        <p>Decision-Support System untuk Optimalisasi Kapasitas 3C (Colo, Connect, Compute AI) & Monetisasi Aset B2B Infra</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Prototype Notice Banner (Atas)
st.markdown(
    """
    <div class="notice-banner">
        <strong>Prototype Notice:</strong> Segment benchmarks reflect 2025 TelkomGroup B2B Infra performance.
        Unit economics, MW pricing, and optimization outputs are synthetically modeled for decision-support demonstration.
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("### Navigasi & Konteks")
    st.info(
        "**Prototype Notice:** Segment benchmarks reflect 2025 TelkomGroup B2B Infra performance. "
        "Unit economics, MW pricing, and optimization outputs are synthetically modeled for decision-support demonstration."
    )
    st.markdown(
        """
        **Benchmark Kinerja 2025:**
        - **External Revenue:** +9,2% (Rp8,93T)
        - **Segment Expenses:** +13,8% (Rp46,10T)
        - **Segment Profit:** -36,3% (Rp10,49T)
        - **NeutraDC Utilization:** ~89%
        - **Mitratel:** >40.000 menara, 1,57x tenancy
        - **InfraNexia:** Spin-off Wholesale Fiber
        """
    )

# Load Data Simulasi
portfolio = generate_infra_portfolio(seed=42)
dc_df = portfolio["dc_clusters"]
tower_df = portfolio["tower_portfolio"]
fiber_df = portfolio["fiber_tiers"]

# 3 Tabs Utama
tab1, tab2, tab3 = st.tabs(
    [
        "1. Infra Margin Squeeze Overview",
        "2. Linear Programming 3C Optimizer",
        "3. Mitratel & InfraNexia Asset Monetization",
    ]
)

# ==============================================================================
# TAB 1: INFRA MARGIN SQUEEZE OVERVIEW
# ==============================================================================
with tab1:
    st.subheader("Tekanan Margin Segmen B2B Infra & Kapasitas Data Center (2025)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        label="External Revenue (2025)",
        value="Rp 8.93 T",
        delta="+9.2% YoY (vs Rp 8.18 T)",
    )
    col2.metric(
        label="Segment Expenses (2025)",
        value="Rp 46.10 T",
        delta="+13.8% YoY (vs Rp 40.51 T)",
        delta_color="inverse",
    )
    col3.metric(
        label="Segment Profit (2025)",
        value="Rp 10.49 T",
        delta="-36.3% YoY (vs Rp 16.47 T)",
        delta_color="inverse",
    )
    col4.metric(
        label="NeutraDC Utilization",
        value="~89.0%",
        delta="11.0 MW Expansion Ready (3C AI)",
    )

    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Grafik Perbandingan Pendapatan vs Beban vs Laba (2024 vs 2025)
        fin_df = pd.DataFrame(
            {
                "Metrik": [
                    "External Revenue",
                    "External Revenue",
                    "Segment Expenses",
                    "Segment Expenses",
                    "Segment Profit",
                    "Segment Profit",
                ],
                "Tahun": ["2024", "2025", "2024", "2025", "2024", "2025"],
                "Nilai (Miliar IDR)": [8180, 8929, 40512, 46103, 16467, 10487],
            }
        )
        fig_fin = px.bar(
            fin_df,
            x="Metrik",
            y="Nilai (Miliar IDR)",
            color="Tahun",
            barmode="group",
            title="Tekanan Biaya vs Pertumbuhan Pendapatan B2B Infra (Miliar IDR)",
            color_discrete_map={"2024": "#64748B", "2025": "#0284C7"},
            text_auto=".3s",
        )
        fig_fin.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text="Tahun",
        )
        st.plotly_chart(fig_fin, use_container_width=True)

    with chart_col2:
        # Grafik Kapasitas Terpakai vs Sisa Kapasitas Ekspansi 3C per Klaster
        fig_dc = go.Figure()
        fig_dc.add_trace(
            go.Bar(
                name="Utilized (MW)",
                x=dc_df["Cluster"],
                y=dc_df["Utilized_MW"],
                marker_color="#0F172A",
            )
        )
        fig_dc.add_trace(
            go.Bar(
                name="Available for 3C Expansion (MW)",
                x=dc_df["Cluster"],
                y=dc_df["Available_MW"],
                marker_color="#0284C7",
            )
        )
        fig_dc.update_layout(
            barmode="stack",
            title="Utilisasi Kapasitas NeutraDC & Sisa Ekspansi 3C (Total 100 MW)",
            yaxis_title="Kapasitas (MW)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_dc, use_container_width=True)

    st.dataframe(dc_df, use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 2: LINEAR PROGRAMMING 3C OPTIMIZER
# ==============================================================================
with tab2:
    st.subheader("Optimasi Alokasi Kapasitas 3C (Colo, Connect, Compute AI)")
    st.markdown(
        "Gunakan panel kendala di bawah untuk mensimulasikan alokasi sisa kapasitas ekspansi **MW** "
        "secara matematis menggunakan `scipy.optimize.linprog` guna memaksimalkan *Contribution Margin*."
    )

    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
    with ctrl_col1:
        avail_mw = st.slider(
            "Sisa Kapasitas Ekspansi (MW)",
            min_value=5.0,
            max_value=25.0,
            value=11.0,
            step=0.5,
        )
    with ctrl_col2:
        max_energy_budget = st.slider(
            "Batas Anggaran Energi/Cooling (Miliar IDR/Thn)",
            min_value=50.0,
            max_value=400.0,
            value=140.0,
            step=5.0,
        )
    with ctrl_col3:
        min_ai_quota = st.slider(
            "Minimum Kuota AI Compute (%)",
            min_value=10,
            max_value=80,
            value=30,
            step=5,
        )
    with ctrl_col4:
        tariff_hike_pct = st.slider(
            "Asumsi Kenaikan Tarif Listrik (%)",
            min_value=0,
            max_value=40,
            value=10,
            step=2,
        )

    energy_multiplier = 1.0 + (tariff_hike_pct / 100.0)
    opt_res = optimize_3c_allocation(
        available_mw=avail_mw,
        max_energy_budget_idr_b=max_energy_budget,
        min_ai_quota_pct=float(min_ai_quota),
        energy_cost_multiplier=energy_multiplier,
    )

    st.markdown("---")

    if not opt_res["success"]:
        st.error(opt_res["message"])
    else:
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric(
            "Optimal Contribution Margin",
            f"Rp {opt_res['total_margin_idr_b']:,.1f} B",
            delta=f"+Rp {opt_res['margin_uplift_idr_b']:,.1f} B vs Baseline",
        )
        kpi2.metric(
            "Proyeksi Total Revenue 3C",
            f"Rp {opt_res['total_revenue_idr_b']:,.1f} B",
        )
        kpi3.metric(
            "Total Biaya Energi & Cooling",
            f"Rp {opt_res['total_energy_cost_idr_b']:,.1f} B",
            delta=f"Batas: Rp {max_energy_budget:,.0f} B",
            delta_color="off",
        )
        kpi4.metric(
            "Alokasi AI Compute Optimal",
            f"{opt_res['allocation_mw']['Neutra Compute AI']} MW",
            delta=f"{(opt_res['allocation_mw']['Neutra Compute AI']/avail_mw)*100:.1f}% dari {avail_mw} MW",
        )

        # Sensitivity & Comparison Chart
        comp_df = pd.DataFrame(
            {
                "Layanan 3C": [
                    "Neutra Colo",
                    "Neutra Connect",
                    "Neutra Compute AI",
                    "Neutra Colo",
                    "Neutra Connect",
                    "Neutra Compute AI",
                ],
                "Skenario": [
                    "Baseline (60/25/15)",
                    "Baseline (60/25/15)",
                    "Baseline (60/25/15)",
                    "Optimal (LinProg)",
                    "Optimal (LinProg)",
                    "Optimal (LinProg)",
                ],
                "Alokasi (MW)": [
                    opt_res["baseline_allocation_mw"]["Neutra Colo"],
                    opt_res["baseline_allocation_mw"]["Neutra Connect"],
                    opt_res["baseline_allocation_mw"]["Neutra Compute AI"],
                    opt_res["allocation_mw"]["Neutra Colo"],
                    opt_res["allocation_mw"]["Neutra Connect"],
                    opt_res["allocation_mw"]["Neutra Compute AI"],
                ],
            }
        )

        fig_opt = px.bar(
            comp_df,
            x="Layanan 3C",
            y="Alokasi (MW)",
            color="Skenario",
            barmode="group",
            title="Perbandingan Alokasi Kapasitas: Baseline Tradisional vs Optimasi Matematis",
            color_discrete_map={
                "Baseline (60/25/15)": "#64748B",
                "Optimal (LinProg)": "#0284C7",
            },
            text_auto=True,
        )
        fig_opt.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_opt, use_container_width=True)

# ==============================================================================
# TAB 3: MITRATEL & INFRANEXIA ASSET MONETIZATION SIMULATOR
# ==============================================================================
with tab3:
    st.subheader("Simulator Monetisasi Aset Tower (Mitratel) & Fiber (InfraNexia)")

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        target_tenancy = st.slider(
            "Target Mitratel Tenancy Ratio (Baseline: 1.57x)",
            min_value=1.57,
            max_value=1.80,
            value=1.65,
            step=0.01,
        )
    with sim_col2:
        fiber_uplift_pct = st.slider(
            "Peningkatan Utilisasi Fiber InfraNexia (%)",
            min_value=0,
            max_value=30,
            value=12,
            step=2,
        )

    # Hitung dampak simulasi Mitratel
    sim_tower = tower_df.copy()
    tenancy_delta = target_tenancy - 1.57
    sim_tower["Simulated_Tenancy_Ratio"] = (
        sim_tower["Baseline_Tenancy_Ratio"] + tenancy_delta
    ).round(2)
    sim_tower["Additional_Tenants"] = (
        sim_tower["Tower_Count"] * tenancy_delta
    ).round(0).astype(int)
    # Asumsi tambahan tenant langsung menambah EBITDA tinggi karena opex tower relatif tetap
    sim_tower["Additional_Annual_Margin_IDR_B"] = (
        sim_tower["Additional_Tenants"]
        * sim_tower["Monthly_Lease_Per_Tenant_IDR_M"]
        * 12
        / 1000.0
    ).round(2)

    total_tower_uplift = sim_tower["Additional_Annual_Margin_IDR_B"].sum()

    # Hitung dampak simulasi InfraNexia
    sim_fiber = fiber_df.copy()
    sim_fiber["Simulated_Utilization_Pct"] = (
        sim_fiber["Baseline_Utilization_Pct"] + fiber_uplift_pct
    ).clip(upper=95.0)
    sim_fiber["Additional_Annual_EBITDA_IDR_B"] = (
        sim_fiber["Annual_Revenue_Potential_IDR_B"]
        * (fiber_uplift_pct / 100.0)
        * (sim_fiber["EBITDA_Margin_Pct"] / 100.0)
    ).round(2)

    total_fiber_uplift = sim_fiber["Additional_Annual_EBITDA_IDR_B"].sum()
    total_recovery = total_tower_uplift + total_fiber_uplift

    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Uplift Margin Mitratel (Kolokasi)",
        f"+Rp {total_tower_uplift:,.1f} B / Thn",
        delta=f"Tenancy {target_tenancy:.2f}x",
    )
    m2.metric(
        "Uplift EBITDA InfraNexia (Fiber)",
        f"+Rp {total_fiber_uplift:,.1f} B / Thn",
        delta=f"+{fiber_uplift_pct}% Utilisasi",
    )
    m3.metric(
        "Total Pemulihan Margin Segmen",
        f"+Rp {total_recovery:,.1f} B / Thn",
        delta="Mitigasi Penurunan Laba 2025",
    )

    st.markdown("#### Portofolio Tower Mitratel (Simulasi Kolokasi)")
    st.dataframe(sim_tower, use_container_width=True, hide_index=True)

    st.markdown("#### Portofolio Wholesale Fiber InfraNexia")
    st.dataframe(sim_fiber, use_container_width=True, hide_index=True)

    csv_data = sim_tower.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Simulasi Portofolio Mitratel (CSV)",
        data=csv_data,
        file_name="mitratel_monetization_simulation.csv",
        mime="text/csv",
    )
