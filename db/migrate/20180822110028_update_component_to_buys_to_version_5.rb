class UpdateComponentToBuysToVersion5 < ActiveRecord::Migration[5.2]
  def change
    update_view :component_to_buys, version: 5, revert_to_version: 4
  end
end
