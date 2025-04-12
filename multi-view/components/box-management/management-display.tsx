import ManagementHeader from './management-header';
import ManagementBoxes from './management-boxes';

const mockBoxes = Array.from({ length: 15 }, (_, i) => ({
    id: `box-${i + 1}`,
    name: `${String(i + 1).padStart(2, '0')}号盒子`,
    type: `website-1310168675...${i}`,
    config: `website-1310168675...${i}`,
    isSelected: i < 2,
  }));
  

export default function ManagementDisplay() {
  return (
    <div className="w-full h-screen p-2 bg-gray-100">
      <div className="flex flex-col h-full gap-1 bg-gray-100">
        <ManagementHeader />
        <ManagementBoxes boxes={mockBoxes} />
      </div>
    </div>
  )
}
