from reportapp.models import ReportData, Area


def contact_center_service(date: str):
    data = ReportData.objects.filter(date=date)
    contact_centers = list(Area.objects.order_by().values_list('area_name', flat=True).distinct())
    res = []
    for center in contact_centers:
        i = 0
        contact_center_res = {
            'contact_center': center,
            'scheduled_time': 0,
            'ready': 0,
            'share_ready': 0,
            'adherence': 0,
            'sick_leave': 0,
            'absenteeism': 0
        }
        for d in data:
            if str(d.contact_center) == center:
                contact_center_res['scheduled_time'] += d.scheduled_time
                contact_center_res['ready'] += d.ready
                contact_center_res['share_ready'] += d.share_ready
                contact_center_res['adherence'] += d.adherence
                contact_center_res['sick_leave'] += d.sick_leave
                contact_center_res['absenteeism'] += d.absenteeism
                i += 1

        if i > 0:
            contact_center_res['share_ready'] /= i
            contact_center_res['adherence'] /= i
            res.append(contact_center_res)
    return res


