import { useState } from 'react';

export function usePagination(initialPage = 1, initialSize = 20) {
  const [page, setPage] = useState(initialPage);
  const [size, setSize] = useState(initialSize);

  const nextPage = () => setPage((p) => p + 1);
  const prevPage = () => setPage((p) => Math.max(1, p - 1));
  const goToPage = (n) => setPage(n);
  const changeSize = (s) => { setSize(s); setPage(1); };

  return { page, size, nextPage, prevPage, goToPage, changeSize };
}
