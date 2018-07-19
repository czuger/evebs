class UpdateComponentToBuysToVersion3 < ActiveRecord::Migration[5.2]
  def change
    # Because update view want to drop a view we already dropped in previous migration.
    execute 'CREATE VIEW component_to_buys AS SELECT 1;'
    update_view :component_to_buys, version: 3, revert_to_version: 2
  end
end
