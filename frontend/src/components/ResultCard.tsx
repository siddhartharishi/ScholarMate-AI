import { Card } from "@/components/ui/card";

interface ResultCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

const ResultCard = ({ title, children, className = "" }: ResultCardProps) => (
  <Card className={`p-5 border-border/60 shadow-sm bg-card/80 backdrop-blur-sm ${className}`}>
    <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">{title}</h3>
    <div className="text-foreground">{children}</div>
  </Card>
);

export default ResultCard;
