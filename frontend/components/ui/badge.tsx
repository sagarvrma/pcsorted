import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "border-zinc-700 bg-zinc-800 text-zinc-300",
        ebay: "border-amber-500/20 bg-amber-500/10 text-amber-400",
        bestbuy: "border-blue-500/20 bg-blue-500/10 text-blue-400",
        newegg: "border-orange-500/20 bg-orange-500/10 text-orange-400",
        walmart: "border-sky-500/20 bg-sky-500/10 text-sky-400",
        bhphoto: "border-purple-500/20 bg-purple-500/10 text-purple-400",
        new: "border-emerald-500/20 bg-emerald-500/10 text-emerald-400",
        refurbished: "border-yellow-500/20 bg-yellow-500/10 text-yellow-400",
        used: "border-zinc-600/30 bg-zinc-700/20 text-zinc-400",
        spec: "border-zinc-700/50 bg-zinc-800/80 text-zinc-300 font-normal",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
