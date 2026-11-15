import numpy as np
import pandas as pd
from scipy.optimize import linprog


def generate_infra_portfolio(seed: int = 42) -> dict:
    """
    Menghasilkan dataset simulasi portofolio aset infrastruktur B2B (Data Center,
    Tower Mitratel, dan Wholesale Fiber InfraNexia) berbasis benchmark 2025.

    Catatan: Parameter harga jual per MW, biaya listrik/pendinginan per MW,
    dan proyeksi margin adalah asumsi model simulasi untuk demonstrasi optimasi.
    """
    rng = np.random.default_rng(seed)

    # 1. Portofolio Klaster Data Center NeutraDC (Total ~100 MW, Utilisasi ~89%)
    dc_clusters = pd.DataFrame(
        [
            {
                "Cluster": "Cikarang Campus 1",
                "Tier": "Tier III/IV",
                "Total_Capacity_MW": 32.0,
                "Utilized_MW": 29.8,
                "Primary_Service": "Neutra Colo",
                "PUE": 1.55,
            },
            {
                "Cluster": "Cikarang Campus 2 (AI Ready)",
                "Tier": "Tier IV Hyperscale",
                "Total_Capacity_MW": 28.0,
                "Utilized_MW": 23.5,
                "Primary_Service": "Neutra Compute AI",
                "PUE": 1.32,
            },
            {
                "Cluster": "Batam Hyperscale DC",
                "Tier": "Tier IV Hyperscale",
                "Total_Capacity_MW": 22.0,
                "Utilized_MW": 18.7,
                "Primary_Service": "Neutra Compute AI",
                "PUE": 1.30,
            },
            {
                "Cluster": "Surabaya & Edge Nodes",
                "Tier": "Tier III",
                "Total_Capacity_MW": 18.0,
                "Utilized_MW": 17.0,
                "Primary_Service": "Neutra Connect",
                "PUE": 1.62,
            },
        ]
    )
    dc_clusters["Available_MW"] = (
        dc_clusters["Total_Capacity_MW"] - dc_clusters["Utilized_MW"]
    ).round(2)
    dc_clusters["Utilization_Pct"] = (
        (dc_clusters["Utilized_MW"] / dc_clusters["Total_Capacity_MW"]) * 100
    ).round(1)

    # 2. Portofolio Tower Mitratel (>40.000 menara, baseline tenancy ratio 1.57x)
    regions = ["Jawa & Bali", "Sumatra", "Kalimantan", "Sulawesi & Nusra", "Papua & Maluku"]
    tower_counts = [18200, 10400, 5600, 4600, 1700]  # Total = 40.500 menara
    tenancy_ratios = [1.66, 1.54, 1.48, 1.46, 1.39]

    tower_portfolio = pd.DataFrame(
        {
            "Region": regions,
            "Tower_Count": tower_counts,
            "Baseline_Tenancy_Ratio": tenancy_ratios,
            "Monthly_Lease_Per_Tenant_IDR_M": [11.5, 11.2, 11.8, 11.4, 12.6],
            "Opex_Per_Tower_IDR_M": [4.2, 4.5, 4.9, 4.8, 5.6],
        }
    )
    tower_portfolio["Total_Tenants"] = (
        tower_portfolio["Tower_Count"] * tower_portfolio["Baseline_Tenancy_Ratio"]
    ).round(0).astype(int)

    # 3. Portofolio Wholesale Fiber Connectivity (InfraNexia Spin-Off Tiers)
    fiber_tiers = pd.DataFrame(
        {
            "Asset_Tier": [
                "Backbone Terestrial (Java-Sumatra)",
                "Submarine Cable & International Gateway",
                "Metro Fiber & FTTT (Tower Backhaul)",
                "Enterprise Dark Fiber & Wavelength",
            ],
            "Route_Km": [48500, 32000, 64000, 21500],
            "Baseline_Utilization_Pct": [74.0, 68.0, 61.0, 52.0],
            "Annual_Revenue_Potential_IDR_B": [2450.0, 1850.0, 2100.0, 1250.0],
            "EBITDA_Margin_Pct": [58.0, 62.0, 54.0, 65.0],
        }
    )

    return {
        "dc_clusters": dc_clusters,
        "tower_portfolio": tower_portfolio,
        "fiber_tiers": fiber_tiers,
    }


def optimize_3c_allocation(
    available_mw: float,
    max_energy_budget_idr_b: float,
    min_ai_quota_pct: float,
    energy_cost_multiplier: float,
) -> dict:
    """
    Menggunakan scipy.optimize.linprog untuk memaksimalkan Contribution Margin
    dari alokasi sisa kapasitas ekspansi (MW) ke 3 layanan:
      0: Neutra Colo
      1: Neutra Connect
      2: Neutra Compute (AI Fabric)

    Asumsi Unit Economics Simulasi (per MW per Tahun dalam Miliar IDR):
    - Neutra Colo       : Revenue 18.0B, Base Energy/Cooling Cost 6.5B, Non-Energy Opex 3.5B
    - Neutra Connect    : Revenue 22.0B, Base Energy/Cooling Cost 4.0B, Non-Energy Opex 5.0B
    - Neutra Compute AI : Revenue 38.0B, Base Energy/Cooling Cost 14.5B, Non-Energy Opex 6.5B
    """
    # Parameter simulasi (Miliar IDR / MW / Tahun)
    revenues = np.array([18.0, 22.0, 38.0])
    base_energy_costs = np.array([6.5, 4.0, 14.5])
    non_energy_opex = np.array([3.5, 5.0, 6.5])

    # Dampak kenaikan tarif listrik terhadap biaya energi & pendinginan
    energy_costs = base_energy_costs * energy_cost_multiplier
    unit_margins = revenues - energy_costs - non_energy_opex

    # linprog melakukan minimisasi, sehingga kita minimalkan -unit_margins
    c = -unit_margins

    # Kendala Pertidaksamaan (A_ub @ x <= b_ub):
    # 1. Total MW <= available_mw
    # 2. Total Biaya Energi <= max_energy_budget_idr_b
    # 3. Kuota minimum AI Compute: x2 >= (min_ai_quota_pct / 100) * available_mw
    #    => -x2 <= -(min_ai_quota_pct / 100) * available_mw
    # 4. Diversifikasi minimum Colo & Connect agar ekosistem seimbang:
    #    x0 >= 0.10 * available_mw  => -x0 <= -0.10 * available_mw
    #    x1 >= 0.10 * available_mw  => -x1 <= -0.10 * available_mw
    min_ai_mw = (min_ai_quota_pct / 100.0) * available_mw
    min_colo_mw = 0.10 * available_mw
    min_connect_mw = 0.10 * available_mw

    A_ub = np.array(
        [
            [1.0, 1.0, 1.0],
            [energy_costs[0], energy_costs[1], energy_costs[2]],
            [0.0, 0.0, -1.0],
            [-1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
        ]
    )
    b_ub = np.array(
        [
            available_mw,
            max_energy_budget_idr_b,
            -min_ai_mw,
            -min_colo_mw,
            -min_connect_mw,
        ]
    )

    bounds = [(0, available_mw), (0, available_mw), (0, available_mw)]

    result = linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    if result.success:
        alloc = result.x
        total_margin = float(np.dot(unit_margins, alloc))
        total_revenue = float(np.dot(revenues, alloc))
        total_energy_cost = float(np.dot(energy_costs, alloc))

        # Skenario Baseline (alokasi merata / tradisional: 60% Colo, 25% Connect, 15% AI)
        baseline_alloc = np.array([0.60, 0.25, 0.15]) * available_mw
        baseline_margin = float(np.dot(unit_margins, baseline_alloc))
        baseline_energy = float(np.dot(energy_costs, baseline_alloc))

        return {
            "success": True,
            "message": "Solusi optimal matematis ditemukan.",
            "allocation_mw": {
                "Neutra Colo": round(float(alloc[0]), 2),
                "Neutra Connect": round(float(alloc[1]), 2),
                "Neutra Compute AI": round(float(alloc[2]), 2),
            },
            "unit_margins": {
                "Neutra Colo": round(float(unit_margins[0]), 2),
                "Neutra Connect": round(float(unit_margins[1]), 2),
                "Neutra Compute AI": round(float(unit_margins[2]), 2),
            },
            "total_margin_idr_b": round(total_margin, 2),
            "total_revenue_idr_b": round(total_revenue, 2),
            "total_energy_cost_idr_b": round(total_energy_cost, 2),
            "baseline_allocation_mw": {
                "Neutra Colo": round(float(baseline_alloc[0]), 2),
                "Neutra Connect": round(float(baseline_alloc[1]), 2),
                "Neutra Compute AI": round(float(baseline_alloc[2]), 2),
            },
            "baseline_margin_idr_b": round(baseline_margin, 2),
            "baseline_energy_cost_idr_b": round(baseline_energy, 2),
            "margin_uplift_idr_b": round(total_margin - baseline_margin, 2),
        }
    else:
        return {
            "success": False,
            "message": (
                "Kendala terlalu ketat (Infeasible): Anggaran energi tidak mencukupi "
                "untuk memenuhi kuota minimum AI Compute dan diversifikasi minimum Colo/Connect "
                "pada kapasitas MW serta tarif listrik saat ini. Naikkan batas anggaran energi "
                "atau turunkan kuota minimum AI Compute."
            ),
        }
