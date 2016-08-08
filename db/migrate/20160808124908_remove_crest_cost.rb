class RemoveCrestCost < ActiveRecord::Migration
  def change
    drop_table :crest_costs
  end
end
