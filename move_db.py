from sqlalchemy import text, insert, Index

from app.core.database import SqlSession, engine, metadata
from app.model.assembler import convert_vo, convert_swtiches
from app.model.domain import KeyboardSwitch, T_switches

if __name__ == '__main__':
    # metadata.create_all(engine, tables=[T_switches])
    # index = Index('uk_stor_loc', T_switches.c.stor_loc_box, T_switches.c.stor_loc_row, T_switches.c.stor_loc_col, unique=True)
    # index.create(engine)

    with SqlSession() as session:
        session.execute(
            text('delete from switches')
        )
        list = session.fetchall(text('select * from keyboard_switch'), KeyboardSwitch)
        mkslist = [convert_swtiches(i) for i in list]
        split_lists = [mkslist[i: i + 100] for i in range(0, len(mkslist), 100)]

        # 打印结果以验证
        for i, split_list in enumerate(split_lists):
            session.execute(
                insert(T_switches).values([m.dict() for m in split_list])
            )
        for i, split_list in enumerate(split_lists):
            print(f"Array {i + 1}: Length {len(split_list)}")




