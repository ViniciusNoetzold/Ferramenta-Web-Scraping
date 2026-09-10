import AnalysisClient from "./AnalysisClient";

export function generateStaticParams() {
  return [{ id: "preview" }];
}

export default function Page() {
  return <AnalysisClient />;
}
