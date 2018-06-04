class RemoveCrestCost < ActiveRecord::Migration[4.2]
  def change
    drop_table :crest_costs
  end
end
