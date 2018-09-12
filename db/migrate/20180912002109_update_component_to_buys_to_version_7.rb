class UpdateComponentToBuysToVersion7 < ActiveRecord::Migration[5.2]
  def change
    create_view :component_to_buys, version: 7
  end
end
