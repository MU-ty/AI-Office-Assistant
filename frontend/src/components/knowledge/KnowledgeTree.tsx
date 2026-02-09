
import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, FileText, Trash2 } from 'lucide-react';
import { Directory } from '../../modules/knowledge/types';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface KnowledgeTreeProps {
  directories: Directory[];
  selectedDirId: number | null;
  onSelectDirectory: (dirId: number | null) => void;
  onCreateDirectory?: (parentId: number | null) => void;
  onDeleteDirectory?: (dirId: number) => void;
}

const TreeNode = ({
  node,
  selectedDirId,
  onSelect,
  onDelete,
  level = 0
}: {
  node: Directory;
  selectedDirId: number | null;
  onSelect: (id: number) => void;
  onDelete?: (id: number) => void;
  level?: number;
}) => {
  const [expanded, setExpanded] = useState(false);
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = selectedDirId === node.id;

  const handleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    setExpanded(!expanded);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
        onDelete(node.id);
    }
  };

  return (
    <div className="select-none group/node">
      <div
        className={cn(
          "flex items-center py-1 px-2 rounded-md cursor-pointer hover:bg-slate-100 text-sm",
          isSelected && "bg-blue-50 text-blue-600 font-medium"
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => onSelect(node.id)}
      >
        <div
          className={cn("mr-1 p-0.5 rounded-sm hover:bg-slate-200 transition-colors", !hasChildren && "invisible")}
          onClick={handleExpand}
        >
          {expanded ? <ChevronDown className="w-3 h-3 text-slate-500" /> : <ChevronRight className="w-3 h-3 text-slate-500" />}
        </div>
        <Folder className={cn("w-4 h-4 mr-2", isSelected ? "text-blue-500 fill-blue-100" : "text-slate-400 fill-slate-50")} />
        <span className="truncate flex-1">{node.name}</span>
        
        {onDelete && (
            <div 
                className="opacity-0 group-hover/node:opacity-100 p-1 hover:bg-red-50 hover:text-red-500 rounded transition-all"
                onClick={handleDelete}
                title="删除目录"
            >
                <Trash2 className="w-3 h-3" />
            </div>
        )}
      </div>
      
      {expanded && hasChildren && (
        <div>
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              selectedDirId={selectedDirId}
              onSelect={onSelect}
              onDelete={onDelete}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const KnowledgeTree = ({
  directories,
  selectedDirId,
  onSelectDirectory,
  onCreateDirectory,
  onDeleteDirectory
}: KnowledgeTreeProps) => {
  return (
    <div className="space-y-1">
      <div
        className={cn(
          "flex items-center py-1 px-2 rounded-md cursor-pointer hover:bg-slate-100 text-sm mb-2",
          selectedDirId === null && "bg-blue-50 text-blue-600 font-medium"
        )}
        onClick={() => onSelectDirectory(null)}
      >
        <div className="w-4 mr-1" /> {/* Spacer for chevron alignment */}
        <FileText className={cn("w-4 h-4 mr-2", selectedDirId === null ? "text-blue-500" : "text-slate-400")} />
        <span className="flex-1">全部文档</span>
      </div>

      {directories.map((dir) => (
        <TreeNode
          key={dir.id}
          node={dir}
          selectedDirId={selectedDirId}
          onSelect={onSelectDirectory}
          onDelete={onDeleteDirectory}
        />
      ))}
      
      {directories.length === 0 && (
        <div className="px-8 py-4 text-xs text-slate-400 text-center border border-dashed border-slate-200 rounded-md">
            暂无目录结构
        </div>
      )}
    </div>
  );
};
