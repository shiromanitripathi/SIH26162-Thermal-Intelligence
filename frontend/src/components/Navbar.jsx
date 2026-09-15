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
            { label: "Command Center", path: "/" },
            { label: "Live Activity", path: "/" },
            { label: "System Status", path: "/" },
        ],
    },
    {
        label: "EXPLORE",
        icon: Map,
        items: [
            { label: "Thermal Map", path: "/map" },
            { label: "Hotspot Search", path: "/events" },
            { label: "Event Explorer", path: "/events" },
            { label: "Persistent Sources", path: "/analysis" },
        ],
    },
    {
        label: "ANALYSIS",
        icon: BrainCircuit,
        items: [
            { label: "AI Assessment", path: "/analysis" },
            { label: "Thermal History", path: "/analysis" },
            { label: "Persistence", path: "/analysis" },
            { label: "Recurrence", path: "/analysis" },
            { label: "Context Intelligence", path: "/analysis" },
        ],
    },
    {
        label: "INTELLIGENCE",
        icon: BarChart3,
        items: [
            { label: "District Intelligence", path: "/intelligence" },
            { label: "Regional Trends", path: "/intelligence" },
            { label: "Priority Sources", path: "/intelligence" },
        ],
    },
    {
        label: "REPORTS",
        icon: FileText,
        items: [
            { label: "Investigation Report", path: "/reports" },
            { label: "Saved Investigations", path: "/reports" },
            { label: "Export / Print", path: "/reports" },
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
                                            to={item.path}
                                            className="dropdown-item"
                                            onClick={() =>
                                                setOpenMenu(null)
                                            }
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