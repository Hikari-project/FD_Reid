'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import EditBoxDialog from './edit-box-dialog';

export interface BoxData {
  id: string;
  name: string;
  type: string;
  config: string; 
  isSelected: boolean;
}

interface BoxCardProps {
  box: BoxData;
  onSelectToggle: (id: string) => void;
  onDetailsClick: (id: string) => void;
  onEditClick: (box: BoxData) => void;
}

function BoxCard({ box, onSelectToggle, onDetailsClick, onEditClick }: BoxCardProps) {
  return (
    <Card className="break-inside-avoid">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
            <CardTitle className="text-lg font-semibold">{box.name}</CardTitle>
            <Checkbox
                id={`select-${box.id}`}
                checked={box.isSelected}
                onCheckedChange={() => onSelectToggle(box.id)}
                aria-label={`Select ${box.name}`}
            />
        </div>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground pb-3">
        <p className="mb-1 truncate">区域类型: <Badge variant="secondary" className="ml-1">{box.type}</Badge></p>
        <p className="truncate">盒子配置: <Badge variant="secondary" className="ml-1">{box.config}</Badge></p>
      </CardContent>
      <CardFooter className="flex justify-end gap-2 pt-0">
        <Button variant="outline" size="sm"  onClick={() => onDetailsClick(box.id)}>详情</Button>
        <Button variant="default" size="sm" className='bg-blue-500 hover:bg-blue-600 text-white' onClick={() => onEditClick(box)}>编辑</Button> {/* Pass box here */}
      </CardFooter>
    </Card>
  );
}

interface ManagementBoxesProps {
  boxes: BoxData[];
}

export default function ManagementBoxes({ boxes }: ManagementBoxesProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingBox, setEditingBox] = useState<BoxData | null>(null);

  const handleSelectToggle = (id: string) => {
      console.log("Toggle selection for:", id);
  };

  const handleDetailsClick = (id: string) => {
      console.log("Details for:", id);
  };

  const handleEditClick = (boxToEdit: BoxData) => {
      console.log("Edit for:", boxToEdit.id);
      setEditingBox(boxToEdit);
      setIsEditDialogOpen(true);
  };

  const handleSaveChanges = (updatedBox: BoxData) => {
      console.log("Saving changes for:", updatedBox);
      setIsEditDialogOpen(false);
  };

  return (
    <>
      <div className="flex flex-wrap gap-6 bg-gray-100 overflow-y-auto px-3">
        {boxes.length === 0 ? (
          <p className="text-center text-muted-foreground col-span-full">没有找到盒子。</p>
        ) : (
          boxes.map((box) => (
            <BoxCard
              key={box.id}
              box={box}
              onSelectToggle={handleSelectToggle}
              onDetailsClick={handleDetailsClick}
              onEditClick={handleEditClick}
            />
          ))
        )}
      </div>

      <EditBoxDialog
        box={editingBox}
        isOpen={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
      />
    </>
  );
} 