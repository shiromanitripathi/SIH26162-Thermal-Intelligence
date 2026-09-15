import {
    Activity,
    Flame,
    Radio,
    ShieldCheck,
} from "lucide-react";

const icons = {
    activity: Activity,
    thermal: Flame,
    satellite: Radio,
    system: ShieldCheck,
};

function StatCard({
    label,
    value = "—",
    description = "Not available yet",
    type = "activity",
}) {
    const Icon = icons[type] || Activity;

    return (
        <div className="stat-card">
            <div className="stat-card-top">
                <div className="stat-icon">
                    <Icon size={19} />
                </div>

                <span className="stat-label">
                    {label}
                </span>
            </div>

            <div className="stat-value">
                {value}
            </div>

            <div className="stat-description">
                {description}
            </div>
        </div>
    );
}

export default StatCard;