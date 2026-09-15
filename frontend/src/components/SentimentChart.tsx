import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

type Props = {
  data: { name: string; value: number }[];
};

const COLORS: Record<string, string> = {
  positive: "#22c55e",
  very_positive: "#10b981",
  negative: "#ef4444",
  very_negative: "#dc2626",
  neutral: "#eab308",
};

const LABELS: Record<string, string> = {
  positive: "إيجابي",
  very_positive: "إيجابي جداً",
  negative: "سلبي",
  very_negative: "سلبي جداً",
  neutral: "حيادي",
};

export default function SentimentChart({ data }: Props) {
  const total = data.reduce((s, d) => s + d.value, 0);

  return (
    <>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              dataKey="value"
              data={data}
              innerRadius={70}
              outerRadius={110}
              paddingAngle={3}
              stroke="rgba(255,255,255,0.1)"
            >
              {data.map((d, i) => (
                <Cell key={i} fill={COLORS[d.name] || "#6366f1"} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "rgba(15,20,40,0.9)",
                border: "1px solid rgba(255,255,255,0.15)",
                borderRadius: 12,
                color: "#e8edf7",
              }}
              formatter={(v: number) => [
                `${v} (${total ? ((v / total) * 100).toFixed(1) : 0}%)`,
                "العدد",
              ]}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-legend">
        {data.map((d) => (
          <span key={d.name}>
            <i
              className="stat-dot"
              style={{ background: COLORS[d.name] || "#6366f1" }}
            />
            {LABELS[d.name] || d.name}: {d.value}
          </span>
        ))}
      </div>
    </>
  );
}
