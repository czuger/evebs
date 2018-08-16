class UserToUserDuplicationRequest < ApplicationRecord

  SALES_ORDERS = 1
  PRODUCTION_LIST = 2

  belongs_to :sender, class_name: 'User'
  belongs_to :receiver, class_name: 'User'

  def duplication_type_to_s
    s = { 1 => 'Sales orders', 2 => 'Production list' }
    s[ duplication_type ]
  end

end
