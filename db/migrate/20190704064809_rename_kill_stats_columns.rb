class RenameKillStatsColumns < ActiveRecord::Migration[5.2]
  def change
    rename_column :universe_systems, :kill_stats_last_week, :kill_stats_current_month
  end
end
