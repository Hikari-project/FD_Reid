'use client';

import React from 'react';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Input } from "@/components/ui/input";

interface BoxSelectionPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalItems: number;
}

export default function BoxSelectionPagination({
  currentPage,
  totalPages,
  onPageChange,
  totalItems,
}: BoxSelectionPaginationProps) {

  const getPaginationItems = () => {
    const items: React.ReactNode[] = [];
    const maxPagesToShow = 5;
    const halfMaxPages = Math.floor(maxPagesToShow / 2);

    if (totalPages <= maxPagesToShow + 2) {
      for (let i = 1; i <= totalPages; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink
              href="#"
              onClick={(e) => { e.preventDefault(); onPageChange(i); }}
              isActive={currentPage === i}
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        );
      }
    } else {
      items.push(
        <PaginationItem key={1}>
          <PaginationLink href="#" onClick={(e) => { e.preventDefault(); onPageChange(1); }} isActive={currentPage === 1}>1</PaginationLink>
        </PaginationItem>
      );

      if (currentPage > halfMaxPages + 2) {
        items.push(<PaginationEllipsis key="start-ellipsis" />);
      }

      let startPage = Math.max(2, currentPage - halfMaxPages);
      let endPage = Math.min(totalPages - 1, currentPage + halfMaxPages);

      if (currentPage <= halfMaxPages + 1) {
          endPage = Math.min(totalPages - 1, maxPagesToShow);
      }
      if (currentPage >= totalPages - halfMaxPages) {
          startPage = Math.max(2, totalPages - maxPagesToShow + 1);
      }

      for (let i = startPage; i <= endPage; i++) {
        items.push(
          <PaginationItem key={i}>
            <PaginationLink href="#" onClick={(e) => { e.preventDefault(); onPageChange(i); }} isActive={currentPage === i}>{i}</PaginationLink>
          </PaginationItem>
        );
      }

      if (currentPage < totalPages - halfMaxPages -1) {
        items.push(<PaginationEllipsis key="end-ellipsis" />);
      }

      items.push(
        <PaginationItem key={totalPages}>
          <PaginationLink href="#" onClick={(e) => { e.preventDefault(); onPageChange(totalPages); }} isActive={currentPage === totalPages}>{totalPages}</PaginationLink>
        </PaginationItem>
      );
    }
    return items;
  };

  const [jumpPage, setJumpPage] = React.useState('');
  const handleJump = () => {
    const pageNum = parseInt(jumpPage, 10);
    if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= totalPages) {
      onPageChange(pageNum);
      setJumpPage('');
    } else {
       alert(`请输入 1 到 ${totalPages} 之间的有效页码`);
       setJumpPage('');
    }
  };

  return (
    <div className="flex items-center justify-center sm:justify-between gap-4 mt-6 text-sm text-muted-foreground">
       <div className='whitespace-nowrap'>共 {totalItems} 条</div>

       <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              href="#"
              onClick={(e) => { e.preventDefault(); if (currentPage > 1) onPageChange(currentPage - 1); }}
              className={currentPage <= 1 ? 'pointer-events-none text-gray-400' : ''}
             />
          </PaginationItem>
          {getPaginationItems()}
          <PaginationItem>
            <PaginationNext
              href="#"
              onClick={(e) => { e.preventDefault(); if (currentPage < totalPages) onPageChange(currentPage + 1); }}
              className={currentPage >= totalPages ? 'pointer-events-none text-gray-400' : ''}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>

       <div className="flex items-center gap-2">
           <span className='whitespace-nowrap'>前往</span>
           <Input
             type="number"
             min="1"
             max={totalPages}
             value={jumpPage}
             onChange={(e) => setJumpPage(e.target.value)}
             onKeyDown={(e) => { if (e.key === 'Enter') handleJump(); }}
             className="h-8 w-16"
             aria-label="跳转页码"
           />
           <span>页</span>
       </div>
    </div>
  );
} 