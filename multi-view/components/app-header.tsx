'use client'

import React, { useMemo } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { HomeIcon, ChevronRightIcon } from '@heroicons/react/24/solid';
import { CircleUserRound } from 'lucide-react';
import { User } from 'next-auth';
import { cn } from '@/lib/utils';

interface BreadcrumbItem {
  label: string;
  href: string;
  isCurrent: boolean;
}

interface BreadcrumbsProps {
  user: User | undefined;
  pathSegmentNames?: Record<string, string>;
  homeLabel?: string;
  containerClassName?: string;
  listClassName?: string;
  itemClassName?: string;
  linkClassName?: string;
  separatorClassName?: string;
  iconClassName?: string;
}

const toTitleCase = (str: string): string => {
  try {
    str = decodeURIComponent(str);
  } catch (e) {
    console.error("Failed to decode segment:", str, e);
  }

  return str
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, char => char.toUpperCase());
};


export function Breadcrumbs({
  user,
  pathSegmentNames = {},
  homeLabel = "首页",
  containerClassName = "text-sm text-gray-600",
  listClassName = "flex items-center space-x-1 md:space-x-2",
  itemClassName = "flex items-center",
  linkClassName = "hover:text-blue-600 hover:underline",
  separatorClassName = "h-4 w-4 text-gray-400",
  iconClassName = "h-4 w-4 mr-1.5 flex-shrink-0",
}: BreadcrumbsProps) {
  const pathname = usePathname();

  const breadcrumbItems = useMemo<BreadcrumbItem[]>(() => {
    const segments = pathname.split('/').filter(segment => segment !== '');

    const items: BreadcrumbItem[] = [
      {
        label: homeLabel,
        href: '/',
        isCurrent: pathname === '/',
      },
    ];

    let currentPath = '';
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const isLastSegment = index === segments.length - 1;

      const label = pathSegmentNames[segment] || toTitleCase(segment);

      items.push({
        label: label,
        href: currentPath,
        isCurrent: isLastSegment,
      });
    });

    return items;
  }, [pathname, pathSegmentNames, homeLabel]);

  if (breadcrumbItems.length <= 1) {
    return null;
  }

  return (
    <div className="flex items-center justify-between">
      <nav aria-label="Breadcrumb" className={containerClassName}>
        <ol className={listClassName}>
          {breadcrumbItems.map((item, index) => (
            <li key={item.href} className={itemClassName}>
              {index > 0 && (
                <ChevronRightIcon className={separatorClassName} aria-hidden="true" />
              )}

              {index === 0 && (
                <HomeIcon className={iconClassName} aria-hidden="true" />
              )}

              {item.isCurrent ? (
                <span className="font-medium text-gray-800 ml-1" aria-current="page">
                  {item.label}
                </span>
              ) : (
                <Link href={item.href} className={`${linkClassName} ml-1`}>
                  {item.label}
                </Link>
              )}
            </li>
          ))}
        </ol>
      </nav>
      <div className={cn(
        'flex items-center pr-4 gap-2',
        containerClassName
      )}>
        <Image 
          src="/Subtract.png"
          alt="User icon"
          width={20}
          height={20}
          className="mr-2 mt-0.5"
        />
        <span>用户：{user?.name}</span>
        <CircleUserRound />
      </div>
    </div>
  );
}