class UserToUserDuplicationRequest < ApplicationRecord

  SALES_ORDERS = 1
  PRODUCTION_LIST = 2

  DATA = {
      1 => { name: 'Sales orders', sql_file: 'sales_orders', class_name: 'UserSaleOrder' },
      2 => { name: 'Production list', sql_file: 'production_list', class_name: 'ProductionList' }
  }

  belongs_to :sender, class_name: 'User'
  belongs_to :receiver, class_name: 'User'

  def duplication_type_to_s
    DATA[ duplication_type ][ :name ]
  end

  def execute_data_duplication!( user )

    request = File.open( "#{Rails.root}/sql/user_data_duplication/#{duplication_type_sql_file}.sql" ).read

    ActiveRecord::Base.transaction do

      duplication_type_class_name.constantize.where( user_id: user.id ).delete_all

      ActiveRecord::Base.connection.exec_insert( request, duplication_type_sql_file,
                                                 [ [ nil, user.id ],
                                                   [ nil, sender_id ] ] )

      self.destroy
    end
  end

  private

  def duplication_type_sql_file
    DATA[ duplication_type ][ :sql_file ]
  end

  def duplication_type_class_name
    DATA[ duplication_type ][ :class_name ]
  end

end
