class RenameCompenentToComponent < ActiveRecord::Migration[4.2]
  def change
    rename_table :compenents, :components
  end
end
