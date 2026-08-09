'use client';

import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentService } from '@/services/documents';
import { UploadCloud, File, Trash2, Search, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

export default function DocumentsPage() {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: documentService.getDocuments
  });

  const uploadMutation = useMutation({
    mutationFn: documentService.uploadDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    }
  });

  const deleteMutation = useMutation({
    mutationFn: documentService.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    }
  });

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (files: FileList) => {
    setUploading(true);
    try {
      // Just upload the first file for simplicity in this MVP
      await uploadMutation.mutateAsync(files[0]);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const filteredDocs = documents.filter((doc: any) => 
    doc.filename?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Knowledge Base</h1>
          <p className="text-muted-foreground text-sm">Manage documents available for retrieval.</p>
        </div>
      </div>

      <div 
        className={cn(
          "border-2 border-dashed rounded-xl p-10 text-center transition-colors",
          dragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-muted/50",
          uploading ? "opacity-50 cursor-wait" : "cursor-pointer"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input 
          ref={fileInputRef}
          type="file" 
          className="hidden" 
          onChange={handleChange}
          accept=".pdf,.txt,.md,.csv" 
        />
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="p-4 bg-primary/10 text-primary rounded-full">
            {uploading ? <Loader2 className="w-8 h-8 animate-spin" /> : <UploadCloud className="w-8 h-8" />}
          </div>
          <div>
            <p className="text-lg font-medium">
              {uploading ? 'Uploading document...' : 'Click to upload or drag and drop'}
            </p>
            <p className="text-sm text-muted-foreground mt-1">PDF, TXT, MD or CSV (max. 10MB)</p>
          </div>
        </div>
      </div>

      <div className="border rounded-xl bg-card">
        <div className="p-4 border-b flex items-center justify-between">
          <h3 className="font-semibold">Documents ({documents.length})</h3>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search documents..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            />
          </div>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-muted-foreground">
            <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
            <p>Loading documents...</p>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-12 text-center text-muted-foreground">
            <File className="w-12 h-12 mx-auto mb-4 opacity-20" />
            <h3 className="text-lg font-medium text-foreground mb-1">No documents found</h3>
            <p className="text-sm">Upload your first document to start querying it with KnowSphere AI.</p>
          </div>
        ) : (
          <div className="divide-y">
            {filteredDocs.map((doc: any) => (
              <div key={doc.id} className="p-4 flex items-center justify-between hover:bg-muted/50 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-primary/10 text-primary rounded-lg">
                    <File className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-medium text-sm">{doc.filename}</p>
                    <div className="flex items-center text-xs text-muted-foreground space-x-2 mt-1">
                      <span>{doc.chunk_count || 0} chunks</span>
                      <span>•</span>
                      <span>Uploaded {doc.created_at ? formatDistanceToNow(new Date(doc.created_at), { addSuffix: true }) : 'recently'}</span>
                    </div>
                  </div>
                </div>
                <button 
                  onClick={() => deleteMutation.mutate(doc.id)}
                  disabled={deleteMutation.isPending}
                  className="p-2 text-muted-foreground hover:text-red-500 hover:bg-red-500/10 rounded-md transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
