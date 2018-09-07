class UpdateComponentToBuysToVersion6 < ActiveRecord::Migration[5.2]
  def change
    create_view :component_to_buys, version: 6
  end
end
