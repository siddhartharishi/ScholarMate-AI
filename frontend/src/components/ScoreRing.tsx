interface ScoreRingProps {
  value: number;
  max: number;
  label: string;
  size?: number;
}

const ScoreRing = ({ value, max, label, size = 80 }: ScoreRingProps) => {
  const pct = (value / max) * 100;
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;
  const color = pct >= 70 ? "hsl(var(--primary))" : pct >= 40 ? "hsl(40 80% 50%)" : "hsl(0 70% 55%)";

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="hsl(var(--border))" strokeWidth={6} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={color} strokeWidth={6}
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <span className="text-lg font-bold text-foreground -mt-[calc(50%+10px)]" style={{ position: 'relative', top: `-${size / 2 + 10}px`, marginBottom: `-${size / 2}px` }}>
        {value}{max === 1 ? '' : `/${max}`}
      </span>
      <span className="text-xs text-muted-foreground font-medium">{label}</span>
    </div>
  );
};

export default ScoreRing;
