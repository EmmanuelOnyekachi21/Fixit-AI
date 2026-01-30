import type { FC } from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: FC<{ className?: string }>;
  iconColor: string;
  trend?: {
    value: string;
    isPositive: boolean;
  };
}

export function StatsCard({ title, value, icon: Icon, iconColor, trend }: StatsCardProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl hover:shadow-2xl transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-400 mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {trend && (
            <p className={`text-sm mt-2 ${trend.isPositive ? 'text-green-400' : 'text-red-400'}`}>
              {trend.isPositive ? '↑' : '↓'} {trend.value}
            </p>
          )}
        </div>
        <div className={`p-4 rounded-lg ${iconColor}`}>
          <Icon className="h-8 w-8" />
        </div>
      </div>
    </div>
  );
}
