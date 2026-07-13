/* Placeholder Invoice Detail Page */
import { useParams } from "react-router-dom";

export default function InvoiceDetailPage() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h1 className="text-2xl font-bold text-foreground mb-2">
        Invoice #{id}
      </h1>
      <p className="text-muted-foreground">
        Invoice details, rule results, and AI explanation will appear here.
      </p>
    </div>
  );
}
