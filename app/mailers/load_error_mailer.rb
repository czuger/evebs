class LoadErrorMailer < ApplicationMailer

  def send_error
    @user = params[:user]
    mail(to: @user[:email], subject: 'Erreur de chargement EVEBS') do |format|
      format.text
    end
  end

end
