class UpdateComponentToBuysToVersion10 < ActiveRecord::Migration[5.2]
  def change
    update_view :component_to_buys, version: 10, revert_to_version: 9
  end
end
