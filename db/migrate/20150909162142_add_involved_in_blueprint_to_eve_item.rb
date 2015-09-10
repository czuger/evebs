class AddInvolvedInBlueprintToEveItem < ActiveRecord::Migration
  def change
    add_column :eve_items, :involved_in_blueprint, :bool, default: false, index: true
  end
end
