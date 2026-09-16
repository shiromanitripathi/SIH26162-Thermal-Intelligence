import { useState } from "react";
import { NavLink } from "react-router-dom";
import {
    ChevronDown,
    Satellite,
    Activity,
    Map,
    BrainCircuit,
    BarChart3,
    FileText,
} from "lucide-react";

const menus = [
    {
        label: "OVERVIEW",
        icon: Activity,
        items: [
            {
                label: "Command Center",
                path: "/",
                hash: "#command-center",
            },
            {
                label: "Live Activity",
                path: "/",
                hash: "#live-activity",
            },
            {
                label: "System Status",
                path: "/",
                hash: "#system-status",
            },
        ],
    },

    {
        label: "EXPLORE",
        icon: Map,
        items: [
            {
                label: "Thermal Map",
                path: "/map",
                hash: "#thermal-map",
            },
            {
                label: "Hotspot Search",
                path: "/events",
                hash: "#hotspot-search",
            },
            {
                label: "Event Explorer",
                path: "/events",
                hash: "#event-explorer",
            },
            {
                label: "Persistent Sources",
                path: "/map",
                hash: "#persistent-sources",
            },
        ],
    },

    {
        label: "ANALYSIS",
        icon: BrainCircuit,
        items: [
            {
                label: "AI Assessment",
                path: "/analysis",
                hash: "#ai-assessment",
            },
            {
                label: "Thermal History",
                path: "/analysis",
                hash: "#thermal-history",
            },
            {
                label: "Persistence",
                path: "/analysis",
                hash: "#persistence",
            },
            {
                label: "Recurrence",
                path: "/analysis",
                hash: "#recurrence",
            },
            {
                label: "Context Intelligence",
                path: "/analysis",
                hash: "#context-intelligence",
            },
        ],
    },

    {
        label: "INTELLIGENCE",
        icon: BarChart3,
        items: [
            {
                label: "District Intelligence",
                path: "/intelligence",
                hash: "#district-intelligence",
            },
            {
                label: "Regional Trends",
                path: "/intelligence",
                hash: "#regional-trends",
            },
            {
                label: "Priority Sources",
                path: "/intelligence",
                hash: "#priority-sources",
            },
        ],
    },

    {
        label: "REPORTS",
        icon: FileText,
        items: [
            {
                label: "Investigation Report",
                path: "/reports",
                hash: "#investigation-report",
            },
            {
                label: "Saved Investigations",
                path: "/reports",
                hash: "#saved-investigations",
            },
            {
                label: "Export / Print",
                path: "/reports",
                hash: "#export-print",
            },
        ],
    },
];

function Navbar() {
    const [openMenu, setOpenMenu] = useState(null);

    return (
        <header className="navbar">

            {/* BRAND */}
            <div className="brand">
                <div className="brand-icon">
                    <Satellite size={21} />
                </div>

                <div>
                    <div className="brand-name">FIRMS</div>
                    <div className="brand-subtitle">
                        THERMAL INTELLIGENCE
                    </div>
                </div>
            </div>

            {/* NAVIGATION */}
            <nav className="nav-menu">
                {menus.map((menu, index) => {
                    const Icon = menu.icon;
                    const isOpen = openMenu === index;

                    return (
                        <div
                            className="nav-dropdown"
                            key={menu.label}
                        >
                            <button
                                className={`nav-button ${isOpen ? "active" : ""
                                    }`}
                                onClick={() =>
                                    setOpenMenu(
                                        isOpen ? null : index
                                    )
                                }
                            >
                                <Icon size={15} />

                                <span>{menu.label}</span>

                                <ChevronDown
                                    size={14}
                                    className={
                                        isOpen
                                            ? "rotate-chevron"
                                            : ""
                                    }
                                />
                            </button>

                            {/* DROPDOWN */}
                            {isOpen && (
                                <div className="dropdown-panel">
                                    {menu.items.map((item) => (
                                        <NavLink
                                            key={item.label}
                                            to={`${item.path}${item.hash || ""}`}
                                            className="dropdown-item"
                                            onClick={() => setOpenMenu(null)}
                                        >
                                            {item.label}
                                        </NavLink>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                })}
            </nav>

            {/* SYSTEM STATUS */}
            <div className="system-status">
                <span className="status-dot" />

                <span>SYSTEM ONLINE</span>

                <span className="project-code">
                    SIH26162
                </span>
            </div>

        </header>
    );
}

export default Navbar;