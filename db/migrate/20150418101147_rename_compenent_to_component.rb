class RenameCompenentToComponent < ActiveRecord::Migration
  def change
    rename_table :compenents, :components
  end
end
