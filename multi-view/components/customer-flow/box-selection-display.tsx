'use client';

import { useRouter } from "next/navigation";
import BoxSelectionGrid from "./box-selection-grid";
import BoxSelectionHeader from "./box-selection-header";
import BoxSelectionPagination from "./box-selection-pagination";

const mockBoxes = Array.from({ length: 6 }, (_, i) => ({
    id: `1`,
    name: `${String(i + 1).padStart(2, '0')}号盒子`,
    imageUrl: `/images/placeholder-image.jpg`,
  }));
  
  const totalBoxes = 20;
  const boxesPerPage = 6;
  

export default function BoxSelectionDisplay() {
    const router = useRouter();
  
    const handleBoxSelect = (boxId: string) => {
      console.log("Selected box ID (URL encoded):", encodeURIComponent(boxId));
      router.push(`/annotation/${encodeURIComponent(boxId)}`);
    };
  
    const handlePageChange = (page: number) => {
        console.log("Change to page:", page);
    };

  return (
    <div className="w-full h-full p-2 bg-gray-100">
      <div className="flex flex-col h-full gap-2 bg-white p-4 rounded-md shadow-sm">
        <header className="text-3xl flex justify-center items-center font-bold p-4">盒子配置</header>
        <BoxSelectionHeader />
        <BoxSelectionGrid boxes={mockBoxes} onBoxSelect={handleBoxSelect} />
        <BoxSelectionPagination
            currentPage={1}
            totalPages={Math.ceil(totalBoxes / boxesPerPage)}
            onPageChange={handlePageChange}
            totalItems={totalBoxes}
            />
      </div>
    </div>
  );
}
