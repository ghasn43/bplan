import { SummaryCard } from '@/components/SummaryCard'
import { useFixedAssetSummary } from '@/api/fixedAssetsApi'
import { formatCurrency } from '@/utils/format'

export function AssetSummaryCards({ projectId }: { projectId: string }) {
  const { data } = useFixedAssetSummary(projectId)
  const cur = data?.currency ?? 'USD'
  return (
    <div className="stat-grid">
      <SummaryCard label="Total Asset Cost" accent="blue" value={formatCurrency(data?.total_asset_cost ?? 0, cur)} />
      <SummaryCard label="Annual Depreciation" accent="amber" value={formatCurrency(data?.annual_depreciation ?? 0, cur)} help="Total straight-line depreciation per full year." />
      <SummaryCard label="Net Book Value" accent="green" value={formatCurrency(data?.net_book_value ?? 0, cur)} help="Cost less accumulated depreciation at the end of the plan." />
      <SummaryCard label="Active Assets" accent="slate" value={data?.active_assets ?? 0} />
      <SummaryCard label="Loan-financed" accent="slate" value={data?.loan_financed_assets ?? 0} />
      <SummaryCard label="Software / Intangible" accent="blue" value={data?.software_intangible_assets ?? 0} />
    </div>
  )
}
