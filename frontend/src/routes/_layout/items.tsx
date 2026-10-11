import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useMemo, useState } from "react"

import { ItemsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddItem from "@/components/Items/AddItem"
import { getColumns } from "@/components/Items/columns"
import PendingItems from "@/components/Pending/PendingItems"
import { Input } from "@/components/ui/input"
import { useDebounce } from "@/hooks/useDebounce"

function getItemsQueryOptions() {
  return {
    queryFn: async () =>
      (await ItemsService.readItems({ query: { skip: 0, limit: 100 } })).data,
    queryKey: ["items"],
  }
}

export const Route = createFileRoute("/_layout/items")({
  component: Items,
  head: () => ({
    meta: [
      {
        title: "Items - FastAPI Template",
      },
    ],
  }),
})

function ItemsTableContent({ query }: { query: string }) {
  const { data: items } = useSuspenseQuery(getItemsQueryOptions())
  const columns = useMemo(() => getColumns(query), [query])

  const needle = query.toLowerCase()
  const filtered = items.data.filter(
    (item) =>
      item.title.toLowerCase().includes(needle) ||
      (item.description ?? "").toLowerCase().includes(needle),
  )

  if (filtered.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any items yet</h3>
        <p className="text-muted-foreground">Add a new item to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={filtered} />
}

function ItemsTable({ query }: { query: string }) {
  return (
    <Suspense fallback={<PendingItems />}>
      <ItemsTableContent query={query} />
    </Suspense>
  )
}

function Items() {
  const [query, setQuery] = useState("")
  const debouncedQuery = useDebounce(query)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Items</h1>
          <p className="text-muted-foreground">Create and manage your items</p>
        </div>
        <AddItem />
      </div>
      <div className="relative max-w-sm">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search items…"
          className="pl-8"
        />
      </div>
      <ItemsTable query={debouncedQuery} />
    </div>
  )
}
