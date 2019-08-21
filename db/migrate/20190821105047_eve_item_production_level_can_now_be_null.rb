class EveItemProductionLevelCanNowBeNull < ActiveRecord::Migration[5.2]
  def change
    change_column :eve_items, :production_level, :integer, limit: 2, null: true, default: nil
  end
end
