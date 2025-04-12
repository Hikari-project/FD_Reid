import AnnotationDisplay from "@/components/customer-flow/annotation-display";

export default function Page({ params }: { params: { id: string } }) {
  return (
    <div className="w-full h-full">
      <AnnotationDisplay boxId={params.id} />
    </div>
  )
}
