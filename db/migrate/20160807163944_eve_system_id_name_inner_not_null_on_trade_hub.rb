class EveSystemIdNameInnerNotNullOnTradeHub < ActiveRecord::Migration
  def change
    change_column_null :trade_hubs, :eve_system_id, false
    change_column_null :trade_hubs, :name, false
    change_column_null :trade_hubs, :inner, false
  end
end
