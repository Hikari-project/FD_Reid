import AnnotationDisplay from "@/components/customer-flow/annotation-display";

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <div className="w-full h-full">
      <AnnotationDisplay boxId={id} />
    </div>
  )
}
