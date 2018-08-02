class UpdateComponentToBuysToVersion4 < ActiveRecord::Migration[5.2]
  def change
    update_view :component_to_buys, version: 4, revert_to_version: 3
  end
end
