class RenameComponentToBlueprintComponent < ActiveRecord::Migration[5.2]
  def change
    execute 'ALTER TABLE components RENAME TO blueprint_components'
  end
end
